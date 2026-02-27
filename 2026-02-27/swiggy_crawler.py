import logging
import time
import random
import json
import re
from curl_cffi import requests
from parsel import Selector
from pymongo import MongoClient, errors
import swiggy_settings as settings
from swiggy_parser import SwiggyParser

# ---------- LOGGING SETUP ----------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class SwiggyProductCrawler:
    def __init__(self):
        """Initialize MongoDB client and Session with impersonation."""
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]
        self.subcategory_collection = self.db[settings.MONGO_COLLECTION_SUBCATEGORY]
        self.product_collection = self.db[settings.MONGO_COLLECTION_PRODUCT_DETAILS]
        
        # Create unique index for product URLs
        self.product_collection.create_index("url", unique=True)
        
        self.session = requests.Session()
        logger.info("Product Crawler initialized. Database: %s, Collection: %s", 
                    settings.MONGO_DB, settings.MONGO_COLLECTION_PRODUCT)

    def _make_request(self, url, referer=None):
        """Make a request with curl_cffi, including retries and exponential backoff."""
        attempts = 0
        while attempts < settings.RETRY_MAX_ATTEMPTS:
            try:
                # Use manual bypass headers for first 2 attempts, then fallback to auto rotation
                if attempts < 2:
                    impersonate, headers, cookies = settings.get_manual_config()
                else:
                    impersonate, headers = settings.get_session_config()
                    cookies = None
                
                if referer:
                    headers["Referer"] = referer
                
                response = self.session.get(
                    url,
                    headers=headers,
                    cookies=cookies if attempts < 2 else None,
                    impersonate=impersonate,
                    timeout=settings.REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response
                
                if response.status_code in [403, 401, 429]:
                    logger.warning("Blocked (%s) for %s. Attempt %d/%d", 
                                   response.status_code, url, attempts + 1, settings.RETRY_MAX_ATTEMPTS)
                else:
                    logger.error("HTTP %s for %s", response.status_code, url)
                
            except Exception as e:
                logger.error("Request error for %s: %s", url, e)
            
            attempts += 1
            if attempts < settings.RETRY_MAX_ATTEMPTS:
                wait_time = (settings.RETRY_BACKOFF_FACTOR ** attempts) + random.uniform(2, 5)
                logger.info("Waiting %.2fs before retry...", wait_time)
                time.sleep(wait_time)
            
        return None

    def save_product(self, data):
        """Save unique product data to MongoDB."""
        try:
            self.product_collection.update_one(
                {"url": data["url"]},
                {"$set": data},
                upsert=True
            )
        except errors.PyMongoError as e:
            logger.error("DB Error (product): %s", e)

    def crawl_pdp(self, url, source_url=None):
        """Fetch and parse a product detail page."""
        logger.info("Crawling PDP: %s", url)
        # Use manual config for PDPs to be safe
        impersonate, headers, cookies = settings.get_manual_config()
        
        response = self.session.get(
            url,
            headers=headers,
            cookies=cookies,
            impersonate=impersonate,
            timeout=settings.REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            product_data = SwiggyParser.extract_data(response.text, url)
            if source_url:
                product_data["source_url"] = source_url
            product_data["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
            self.save_product(product_data)
            return True
        else:
            logger.warning("Failed to fetch PDP %s: %s", url, response.status_code)
            return False

    def extract_product_urls(self, source_url):
        """Extract product URLs from a category or subcategory page."""
        logger.info("Fetching products from: %s", source_url)
        response = self._make_request(source_url)
        if not response:
            return

        selector = Selector(text=response.text)
        count = 0
        
        # Selectors for Swiggy Product Cards
        # data-testid="item-collection-card-full" is a strong candidate
        product_links = selector.css('a[data-testid*="item-collection-card"]')
        if not product_links:
            # Fallback to general product path pattern
            product_links = selector.css('a[href*="/instamart/p/"]')

        seen_on_page = set()
        
        for link in product_links:
            url_path = link.attrib.get('href')
            if not url_path or '/instamart/p/' not in url_path:
                continue
                
            full_url = "https://www.swiggy.com" + url_path.split('?')[0]
            
            if full_url in seen_on_page:
                continue
                
            # Attempt to extract product name if available in the anchor
            name = link.css('div[class*="bYyghw"]::text').get() or \
                   link.xpath('.//div[contains(@class, "bYyghw")]/text()').get() or \
                   "Unknown Product"
            # Instead of just saving the URL, we now crawl the PDP
            success = self.crawl_pdp(full_url, source_url=source_url)
            if success:
                count += 1
            
            # Small delay between products
            time.sleep(random.uniform(1, 2))
            
        logger.info("Found %d products on page.", count)

    def run(self, specific_urls=None):
        """Main execution flow."""
        if specific_urls:
            targets = specific_urls
        else:
            # Fetch subcategories from DB to crawl
            try:
                subcats = list(self.subcategory_collection.find({}, {"url": 1}))
                targets = [s["url"] for s in subcats]
            except Exception as e:
                logger.error("Could not fetch subcategories from DB: %s", e)
                return

        if not targets:
            logger.warning("No target URLs found to crawl. Run category scraper first or provide seeds.")
            return

        logger.info("Starting crawl for %d target URLs...", len(targets))
        for url in targets:
            time.sleep(random.uniform(2, 5))
            try:
                self.extract_product_urls(url)
            except Exception as e:
                logger.error("Error processing %s: %s", url, e)

        logger.info("Product crawling finished.")

if __name__ == "__main__":
    # Example: Run on a specific category page to test
    TEST_SEEDS = [
        "https://www.swiggy.com/instamart/city/bangalore/c/tea-coffee-and-more"
    ]
    crawler = SwiggyProductCrawler()
    crawler.run(specific_urls=TEST_SEEDS)
