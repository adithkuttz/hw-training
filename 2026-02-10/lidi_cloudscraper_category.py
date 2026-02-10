import cloudscraper
from parsel import Selector
import logging
from pymongo import MongoClient
import lidl_settings as settings

# ---------------- LOGGING ---------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Category:

    def __init__(self):
        # MongoDB
        self.client = MongoClient("localhost", 27017)
        self.db = self.client[settings.MONGO_DB]
        self.collection = self.db[settings.MONGO_COLLECTION_CATEGORY_CLOUDSCRAPER]
        self.collection.create_index("url", unique=True)

        # Cloudscraper
        self.scraper = cloudscraper.create_scraper()

    def start(self):
        try:
            logger.info("Requesting Homepage: %s", settings.BASE_URL)

            response = self.scraper.get(settings.BASE_URL)
            response.raise_for_status()

            selector = Selector(text=response.text)
            links = selector.xpath("//a")

            logger.info("Total links found: %s", len(links))

            seen_urls = set()

            for link in links:
                text = link.xpath("normalize-space()").get()
                href = link.xpath("@href").get()

                # DEBUG — see all anchor texts
                # logger.info("Anchor Text: %s", text)

                if text and "food" in text.lower():
                    if not href:
                        continue

                    # Build Full URL
                    if href.startswith("http"):
                        url = href
                    else:
                        url = settings.BASE_URL.rstrip("/") + href

                    if url not in seen_urls:
                        seen_urls.add(url)
                        logger.info("Found Category: %s -> %s", text, url)
                        self.save_to_mongo(text, url)

        except Exception as e:
            logger.error("Error during scraping: %s", e)
        finally:
            self.close()

    def save_to_mongo(self, text, url):
        item = {
            "category_name": text.strip(),
            "url": url
        }

        try:
            self.collection.update_one(
                {"url": url},
                {"$set": item},
                upsert=True
            )
            logger.info("Saved to MongoDB")
        except Exception as e:
            logger.error("MongoDB Error: %s", e)

    def close(self):
        if self.client:
            self.client.close()


if __name__ == "__main__":
    crawler = Category()
    crawler.start()
