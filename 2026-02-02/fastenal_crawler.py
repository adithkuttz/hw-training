import requests
import logging
import urllib.parse
import time
import pymongo
from datetime import datetime
import fastenal_settings as settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FastenalPDPCrawler:

    def __init__(self):
        self.endpoint_url = settings.ENDPOINT_URL
        self.headers = settings.HEADERS
        self.cookies = settings.COOKIES

        # MongoDB
        self.client = pymongo.MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.DB_NAME]
        self.product_collection = self.db[settings.PRODUCT_COLLECTION_NAME]

    # -------- PARSE CATEGORY URL --------
    def parse_category_url(self, url):
        parsed = urllib.parse.urlparse(url)
        path_segments = parsed.path.strip("/").split("/")

        l1 = urllib.parse.unquote(path_segments[1])
        l2 = urllib.parse.unquote(path_segments[2])
        l3 = urllib.parse.unquote(path_segments[3])

        query = urllib.parse.parse_qs(parsed.query)

        return {
            "categoryId": query.get("categoryId", [None])[0],
            "productFamilyId": query.get("productFamilyId", [None])[0],
            "categoryLevelOne": l1,
            "categoryLevelTwo": l2,
            "categoryLevelThree": l3,
            "pageUrl": parsed.path
        }

    # -------- FETCH PRODUCTS --------
    def fetch_products(self, context, page):
        payload = {
            "attributeFilters": {},
            "categoryId": context["categoryId"],
            "productFamilyId": context["productFamilyId"],
            "categoryLevelOne": context["categoryLevelOne"],
            "categoryLevelTwo": context["categoryLevelTwo"],
            "categoryLevelThree": context["categoryLevelThree"],
            "pageUrl": context["pageUrl"],
            "page": page,
            "fsi": "1",
            "ignoreCounterBook": True
        }

        response = requests.post(
            self.endpoint_url,
            headers=self.headers,
            cookies=self.cookies,
            json=payload,
            timeout=20
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("productList", [])

        return []

    # -------- SAVE PRODUCT --------
    def save_product(self, sku, category):
        url = f"https://www.fastenal.com/product/details/{sku}"

        self.product_collection.update_one(
            {"url": url},
            {
                "$setOnInsert": {
                    "url": url,
                    "sku": sku,
                    "category": category,
                    "created_at": datetime.now()
                }
            },
            upsert=True
        )

    # -------- MAIN CRAWL --------
    def crawl(self, category_url, limit=100):
        context = self.parse_category_url(category_url)
        page = 1
        total_saved = 0

        while total_saved < limit:
            logger.info(f"Fetching Page {page}")
            products = self.fetch_products(context, page)

            if not products:
                break

            for p in products:
                if total_saved >= limit:
                    break

                sku = p.get("sku")
                if sku:
                    self.save_product(sku, context["categoryLevelThree"])
                    total_saved += 1

            page += 1
            time.sleep(0.4)

        logger.info(f"TOTAL PDP SAVED = {total_saved}")


# -------- RUN --------
if __name__ == "__main__":
    crawler = FastenalPDPCrawler()

    test_url = "https://www.fastenal.com/product/Abrasives/Sanding%20Abrasives%20Products/Fiber%20and%20Sanding%20Discs?productFamilyId=38949&categoryId=609478"

    crawler.crawl(test_url, limit=100)
