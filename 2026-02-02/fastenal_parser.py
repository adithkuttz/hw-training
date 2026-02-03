import re
import html
import pymongo
import logging
import requests
import fastenal_settings as settings

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FastenalParser:

    def __init__(self):
        self.headers = settings.HEADERS
        self.cookies = settings.COOKIES
        self.endpoint_url = settings.ENDPOINT_URL

        # -------- MONGODB --------
        self.client = pymongo.MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.DB_NAME]

        # PDP URL COLLECTION (100 SKUs)
        self.pdp_collection = self.db[settings.PRODUCT_COLLECTION_NAME]

        # PARSED COLLECTION
        self.parsed_collection = self.db["fastenal_parsed_products"]

        # UNIQUE INDEX
        self.parsed_collection.create_index(
            [("url", 1), ("sku", 1)],
            unique=True
        )

        logger.info("Connected to MongoDB")

    # ---------------- API CALL ----------------
    def fetch_product_api(self, doc):

        payload = {
            "attributeFilters": {},
            "categoryId": doc.get("categoryId"),
            "categoryLevelOne": doc.get("categoryLevelOne"),
            "categoryLevelTwo": doc.get("categoryLevelTwo"),
            "categoryLevelThree": doc.get("categoryLevelThree"),
            "pageUrl": doc.get("pageUrl"),
            "productDetails": True,
            "sku": [doc.get("sku")]
        }

        try:
            response = requests.post(
                self.endpoint_url,
                headers=self.headers,
                cookies=self.cookies,
                json=payload,
                timeout=20
            )

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            logger.error(f"API Error {doc.get('sku')}: {e}")

        return None

    # ---------------- HTML CLEAN ----------------
    def clean_html(self, raw_html):
        if not raw_html:
            return ""
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, ' ', raw_html)
        return html.unescape(cleantext).strip()

    # ---------------- PARSE PRODUCT ----------------
    def parse_product_data(self, data, product_url):

        if not data or "productDetail" not in data:
            return None

        detail = data["productDetail"]

        # DESCRIPTION
        notes = detail.get("notes", {})
        desc_parts = []

        for key in [
            "mp_publicNotes",
            "mp_complianceNotes",
            "mp_bulletPoints",
            "mp_applicationUse"
        ]:
            if notes.get(key):
                desc_parts.append(self.clean_html(notes.get(key)))

        full_description = " ".join(desc_parts).strip()

        item = {
            "sku": detail.get("sku"),
            "title": detail.get("mp_des"),
            "brand": detail.get("brNm"),
            "manufacturer": detail.get("mfr"),
            "part_number": detail.get("manufacturerPartNo"),
            "url": product_url,
            "description": full_description,
            "image": detail.get("imgOne"),
            "price": None
        }

        # PRICE
        if "pdd" in detail:
            for p in detail["pdd"]:
                if p.get("dataName") == "Online Price:":
                    item["price"] = p.get("pr")

        return item

    # ---------------- MAIN PARSER ----------------
    def parse(self):

        docs = list(self.pdp_collection.find().limit(100))
        logger.info(f"Parsing {len(docs)} products")

        total_saved = 0

        for doc in docs:
            sku = doc.get("sku")
            url = doc.get("url")

            logger.info(f"Processing SKU {sku}")

            api_data = self.fetch_product_api(doc)

            if not api_data:
                continue

            parsed_data = self.parse_product_data(api_data, url)

            if parsed_data:
                try:
                    self.parsed_collection.update_one(
                        {"sku": sku},
                        {"$set": parsed_data},
                        upsert=True
                    )
                    total_saved += 1
                except Exception as e:
                    logger.error(f"Save Error {sku}: {e}")

        logger.info(f"TOTAL PARSED = {total_saved}")


# ---------------- RUN ----------------
if __name__ == "__main__":
    parser = FastenalParser()
    parser.parse()
