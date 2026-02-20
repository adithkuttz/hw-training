import logging
import time
import random
from curl_cffi import requests
from pymongo import MongoClient
import reelly_settings as settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReellyCrawler:

    def __init__(self):
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]
        self.collection = self.db["reelly_project_urls"]
        self.session = requests.Session()

    def _make_request(self, params):
        url = f"{settings.API_BASE_URL}/projects"

        response = self.session.get(
            url,
            params=params,
            headers=settings.MANUAL_HEADERS,
            impersonate="chrome120",
            timeout=settings.REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            return response.json()

        logger.warning(f"HTTP {response.status_code}")
        return None

    def crawl_projects(self):
        offset = 0
        limit = 24
        total_processed = 0

        while True:
            params = {
                "offset": offset,
                "limit": limit,
                "preferred_area_unit": "sqft"
            }

            logger.info(f"Fetching projects offset={offset}")
            data = self._make_request(params)

            if not data:
                break

            projects = data if isinstance(data, list) else data.get("results", [])
            total = data.get("count", len(projects)) if isinstance(data, dict) else len(projects)

            if not projects:
                break

            for p in projects:
                project_id = p.get("id")
                if project_id:
                    url = f"https://find.reelly.io/projects/{project_id}"

                    self.collection.update_one(
                        {"project_id": project_id},
                        {
                            "$set": {
                                "project_id": project_id,
                                "url": url,
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                            }
                        },
                        upsert=True
                    )

                    total_processed += 1

            logger.info(f"Saved {len(projects)} project URLs")

            if total_processed >= total:
                break

            offset += limit
            time.sleep(random.uniform(1, 3))

        logger.info(f"Crawling completed. Total: {total_processed}")


if __name__ == "__main__":
    crawler = ReellyCrawler()
    crawler.crawl_projects()
