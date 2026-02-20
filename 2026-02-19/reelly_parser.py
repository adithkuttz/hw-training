import logging
import time
import random
from curl_cffi import requests
from pymongo import MongoClient
import reelly_settings as settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReellyParser:

    def __init__(self):
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]
        self.url_collection = self.db["reelly_project_urls"]
        self.product_collection = self.db["reelly_projects"]
        self.session = requests.Session()

    # -----------------------------
    # Safe Value Helper
    # -----------------------------
    def safe_value(self, value):
        """Convert None to empty string"""
        return value if value is not None else ""

    # -----------------------------
    # Request
    # -----------------------------
    def _make_request(self, project_id):
        url = f"{settings.API_BASE_URL}/projects/{project_id}"

        response = self.session.get(
            url,
            headers=settings.MANUAL_HEADERS,
            impersonate="chrome120",
            timeout=settings.REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            return response.json()

        logger.warning(f"Failed {response.status_code} for {project_id}")
        return None

    # -----------------------------
    # Parser
    # -----------------------------
    def parse_projects(self):

        # LIMIT TO 100 PROJECTS ONLY
        urls = list(self.url_collection.find().limit(50))
        logger.info(f"Parsing only {len(urls)} projects")

        for item in urls:
            project_id = item.get("project_id")

            # Skip if already parsed
            if self.product_collection.find_one({"project_id": project_id}):
                logger.info(f"Skipping already parsed {project_id}")
                continue

            logger.info(f"Parsing project {project_id}")
            data = self._make_request(project_id)

            if not data:
                continue

            project_data = {
                "project_id": self.safe_value(data.get("id")),
                "name": self.safe_value(data.get("name")),
                "developer": self.safe_value(data.get("developer_name")),
                "district": self.safe_value(data.get("district")),
                "min_price": self.safe_value(data.get("min_price")),
                "status": self.safe_value(data.get("status")),
                "sale_status": self.safe_value(data.get("sale_status")),
                "construction_end_date": self.safe_value(data.get("construction_end_date")),
                "latitude": self.safe_value(data.get("latitude")),
                "longitude": self.safe_value(data.get("longitude")),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            self.product_collection.update_one(
                {"project_id": project_id},
                {"$set": project_data},
                upsert=True
            )

            time.sleep(random.uniform(1, 2))

        logger.info("Parsing completed.")


if __name__ == "__main__":
    parser = ReellyParser()
    parser.parse_projects()
