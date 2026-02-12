from curl_cffi import requests
from parsel import Selector
from pymongo import MongoClient
from urllib.parse import urljoin
import lidl_settings as settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Category:

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[settings.MONGO_DB]
        self.collection = self.db[settings.MONGO_COLLECTION_CATEGORY_CURL]
        self.collection.create_index("url", unique=True)

    def start(self):
        response = requests.get(settings.BASE_URL, impersonate="chrome110")
        sel = Selector(text=response.text)

        main_links = sel.xpath("//a[contains(@href,'/c/')]")

        for link in main_links:
            name = link.xpath("normalize-space()").get()
            href = link.xpath("@href").get()

            if not name or len(name) < 3:
                continue
            if "privacy" in href or "safety" in href:
                continue

            main_url = urljoin(settings.BASE_URL, href)
            logger.info(f"Main: {name}")
            self.save(name, main_url, "main", None)

            # OPEN CATEGORY
            cat_resp = requests.get(main_url, impersonate="chrome110")
            cat_sel = Selector(text=cat_resp.text)

            sub_links = cat_sel.xpath("//a[contains(@href,'category.id=')]")

            for sub in sub_links:
                sub_name = sub.xpath("normalize-space()").get()
                sub_href = sub.xpath("@href").get()

                if not sub_name or "?" not in sub_href:
                    continue

                sub_url = urljoin(settings.BASE_URL, sub_href)
                logger.info(f"   Sub: {sub_name}")
                self.save(sub_name, sub_url, "sub", name)

        self.close()

    def save(self, name, url, type_, parent):
        self.collection.update_one(
            {"url": url},
            {"$set": {
                "name": name,
                "url": url,
                "type": type_,
                "parent": parent
            }},
            upsert=True
        )

    def close(self):
        self.client.close()

if __name__ == "__main__":
    Category().start()
