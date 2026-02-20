import logging
import time
import random
from curl_cffi import requests
from pymongo import MongoClient, errors
import reelly_settings as settings

# -----------------------------
# LOGGING
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class ReellyCategoryExtractor:

    def __init__(self):
        try:
            self.client = MongoClient(settings.MONGO_URI)
            self.db = self.client[settings.MONGO_DB]
            self.collection = self.db["reelly_categories"]

            # Create unique index
            self.collection.create_index(
                [("type", 1), ("id", 1)],
                unique=True
            )

            self.session = requests.Session()

            logger.info("Reelly Category Extractor initialized.")

        except Exception as e:
            logger.critical(f"Initialization failed: {e}")
            raise

    # -----------------------------
    # REQUEST HANDLER WITH RETRY
    # -----------------------------
    def _make_request(self, endpoint):

        url = f"{settings.API_BASE_URL.rstrip('/')}/{endpoint}"
        logger.info(f"Fetching: {url}")

        attempts = 0

        while attempts < settings.RETRY_MAX_ATTEMPTS:
            try:
                response = self.session.get(
                    url,
                    headers=settings.MANUAL_HEADERS,
                    impersonate="chrome120",
                    timeout=settings.REQUEST_TIMEOUT
                )

                if response.status_code == 200:
                    return response.json()

                logger.warning(
                    f"HTTP {response.status_code} for {url} "
                    f"(Attempt {attempts+1}/{settings.RETRY_MAX_ATTEMPTS})"
                )

            except Exception as e:
                logger.error(f"Request error: {e}")

            attempts += 1
            sleep_time = settings.RETRY_BACKOFF_FACTOR ** attempts
            sleep_time += random.uniform(1, 3)
            logger.info(f"Retrying in {sleep_time:.2f}s...")
            time.sleep(sleep_time)

        logger.error(f"Failed after {settings.RETRY_MAX_ATTEMPTS} attempts.")
        return None

    # -----------------------------
    # DISTRICTS (MAIN CATEGORY)
    # -----------------------------
    def extract_districts(self):

        data = self._make_request("districts?limit=all")

        if not data:
            return []

        districts = data if isinstance(data, list) else data.get("results", [])

        extracted = []

        for d in districts:
            name = d.get("name")
            district_id = d.get("id")

            if name and district_id:
                extracted.append({
                    "type": "district",
                    "id": district_id,
                    "name": name,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })

        logger.info(f"Extracted {len(extracted)} districts")
        return extracted

    # -----------------------------
    # DEVELOPERS (SUB CATEGORY)
    # -----------------------------
    def extract_developers(self):

        data = self._make_request("developers?limit=all")

        if not data:
            return []

        developers = data if isinstance(data, list) else data.get("results", [])

        extracted = []

        for d in developers:
            name = d.get("name")
            dev_id = d.get("id")

            if name and dev_id:
                extracted.append({
                    "type": "developer",
                    "id": dev_id,
                    "name": name,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })

        logger.info(f"Extracted {len(extracted)} developers")
        return extracted

    # -----------------------------
    # SAVE TO DATABASE
    # -----------------------------
    def save_categories(self, categories):

        if not categories:
            logger.warning("No categories to save.")
            return

        saved = 0

        for cat in categories:
            try:
                self.collection.update_one(
                    {"type": cat["type"], "id": cat["id"]},
                    {"$set": cat},
                    upsert=True
                )
                saved += 1
            except errors.PyMongoError as e:
                logger.error(f"DB error: {e}")

        logger.info(f"Saved {saved} categories")

    # -----------------------------
    # RUN
    # -----------------------------
    def run(self):

        logger.info("Starting category extraction...")

        districts = self.extract_districts()
        self.save_categories(districts)

        developers = self.extract_developers()
        self.save_categories(developers)

        logger.info("Category extraction completed successfully.")


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    scraper = ReellyCategoryExtractor()
    scraper.run()
