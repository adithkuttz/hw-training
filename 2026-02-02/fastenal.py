import requests
import logging
import urllib.parse
import time
import fastenal_settings as settings
import pymongo
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FastenalCategoryScraper:

    def __init__(self):
        self.endpoint_url = settings.ENDPOINT_URL
        self.headers = settings.HEADERS
        self.cookies = settings.COOKIES

        self.client = pymongo.MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.DB_NAME]
        self.collection = self.db[settings.COLLECTION_NAME]

        self.root_category_id = settings.ROOT_CATEGORY_ID
        self.root_category_name = settings.ROOT_CATEGORY_NAME

    # ---------- API CALL ----------
    def fetch_categories(self, category_id, payload):
        try:
            response = requests.post(
                self.endpoint_url,
                headers=self.headers,
                cookies=self.cookies,
                json=payload,
                timeout=20
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    return data.get("categoryList", [])
                elif isinstance(data, list):
                    return data
        except Exception as e:
            logger.error(e)
        return []

    # ---------- SCRAPER ----------
    def scrape(self):
        all_urls = set()  # avoid duplicates

        l1_enc = urllib.parse.quote(self.root_category_name)

        l1_payload = {
            "categoryId": self.root_category_id,
            "categoryLevelOne": self.root_category_name,
            "fsi": "1",
            "ignoreCounterBook": True,
            "attributeFilters": {},
            "pageUrl": f"/product/{l1_enc}"
        }

        level2_nodes = self.fetch_categories(self.root_category_id, l1_payload)
        logger.info(f"L2 Count = {len(level2_nodes)}")

        for l2 in level2_nodes:
            l2_name = l2.get("categoryLevelTwo") or l2.get("mp_categoryLabelTwo")
            l2_id = l2.get("categoryId")
            if not l2_name or not l2_id:
                continue

            l2_enc = urllib.parse.quote(l2_name)

            l2_payload = {
                "categoryId": l2_id,
                "categoryLevelOne": self.root_category_name,
                "categoryLevelTwo": l2_name,
                "fsi": "1",
                "ignoreCounterBook": True,
                "attributeFilters": {},
                "pageUrl": f"/product/{l1_enc}/{l2_enc}"
            }

            level3_nodes = self.fetch_categories(l2_id, l2_payload)
            logger.info(f"L3 Count ({l2_name}) = {len(level3_nodes)}")

            for l3 in level3_nodes:
                l3_name = l3.get("categoryLevelThree") or l3.get("mp_categoryLabelThree")
                l3_id = l3.get("categoryId")
                if not l3_name or not l3_id:
                    continue

                print("Processing L3:", l3_name)

                l3_enc = urllib.parse.quote(l3_name)

                # ---- SAVE L3 ALWAYS ----
                l3_url = f"https://www.fastenal.com/product/{l1_enc}/{l2_enc}/{l3_enc}?categoryId={l3_id}"
                all_urls.add(l3_url)

                # ---- CHECK L4 ----
                l3_payload = {
                    "categoryId": l3_id,
                    "categoryLevelOne": self.root_category_name,
                    "categoryLevelTwo": l2_name,
                    "categoryLevelThree": l3_name,
                    "fsi": "1",
                    "ignoreCounterBook": True,
                    "attributeFilters": {},
                    "pageUrl": f"/product/{l1_enc}/{l2_enc}/{l3_enc}"
                }

                level4_nodes = self.fetch_categories(l3_id, l3_payload)

                for l4 in level4_nodes:
                    l4_name = l4.get("categoryLevelFour")
                    l4_id = l4.get("categoryId")
                    if not l4_name or not l4_id:
                        continue

                    l4_enc = urllib.parse.quote(l4_name)

                    l4_url = (
                        f"https://www.fastenal.com/product/"
                        f"{l1_enc}/{l2_enc}/{l3_enc}/{l4_enc}"
                        f"?categoryId={l4_id}"
                    )

                    all_urls.add(l4_url)

                time.sleep(0.1)  # faster

        return list(all_urls)

    # ---------- SAVE DB ----------
    def save_to_db(self, urls):
        for url in urls:
            self.collection.update_one(
                {"url": url},
                {"$setOnInsert": {"url": url, "created_at": datetime.now()}},
                upsert=True
            )


# ---------- RUN ----------
if __name__ == "__main__":
    scraper = FastenalCategoryScraper()
    urls = scraper.scrape()
    scraper.save_to_db(urls)

    print("\nTOTAL URLs =", len(urls))
