import logging
import time
import random
import json
import re
from curl_cffi import requests
from parsel import Selector
from pymongo import MongoClient, errors
import swiggy_settings as settings

# ---------- LOGGING SETUP ----------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class SwiggyCategoryScraper:
    def __init__(self):
        """Initialize MongoDB client and Session with impersonation."""
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]
        self.category_collection = self.db[settings.MONGO_COLLECTION_CATEGORY]
        self.subcategory_collection = self.db[settings.MONGO_COLLECTION_SUBCATEGORY]
        
        # Create unique indexes
        self.category_collection.create_index("url", unique=True)
        self.subcategory_collection.create_index("url", unique=True)
        
        self.session = requests.Session()
        logger.info("Scraper initialized. Database: %s", settings.MONGO_DB)

    def _make_request(self, url, referer=None, is_homepage=False):
        """Make a request with curl_cffi, including retries and exponential backoff."""
        attempts = 0
        while attempts < settings.RETRY_MAX_ATTEMPTS:
            try:
                # Primary strategy: Manual Bypass (if cookies are provided in settings)
                # Fallback: Automatic Rotation after 2 attempts
                if attempts < 2:
                    impersonate, headers, cookies = settings.get_manual_config()
                    logger.debug("Attempt %d: Using Manual Bypass", attempts + 1)
                else:
                    impersonate, headers = settings.get_session_config(is_homepage=is_homepage)
                    cookies = None
                    logger.debug("Attempt %d: Using Automatic Rotation", attempts + 1)
                
                if referer:
                    headers["Referer"] = referer
                elif is_homepage:
                    headers["Referer"] = "https://www.google.com"
                
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

    def save_category(self, data):
        """Save unique main category to MongoDB."""
        try:
            self.category_collection.update_one(
                {"url": data["url"]},
                {"$set": data},
                upsert=True
            )
        except errors.PyMongoError as e:
            logger.error("DB Error (category): %s", e)

    def save_subcategory(self, data):
        """Save unique subcategory to MongoDB."""
        try:
            self.subcategory_collection.update_one(
                {"url": data["url"]},
                {"$set": data},
                upsert=True
            )
        except errors.PyMongoError as e:
            logger.error("DB Error (subcategory): %s", e)

    def extract_main_categories(self):
        """Extract main categories from the Instamart home page."""
        logger.info("Fetching Swiggy Instamart home page...")
        response = self._make_request(settings.BASE_URL, is_homepage=True)
        if not response:
            return []

        categories = []
        
        # 1. Try __NEXT_DATA__ JSON
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', response.text)
        if match:
            try:
                data = json.loads(match.group(1))
                # Navigation for Swiggy Instamart is complex in JSON, 
                # but we can look for collection cards
                widgets = data.get('props', {}).get('pageProps', {}).get('initialData', {}).get('widgets', [])
                for widget in widgets:
                    items = widget.get('data', [])
                    for item in items:
                        link = item.get('link', '')
                        name = item.get('displayName', '') or item.get('nodeName', '')
                        if '/instamart/city/' in link and '/c/' in link:
                            full_url = "https://www.swiggy.com" + link.split('?')[0]
                            categories.append({"name": name, "url": full_url})
            except Exception as e:
                logger.error("Error parsing __NEXT_DATA__: %s", e)

        # 2. CSS Selectors Fallback
        selector = Selector(text=response.text)
        cards = selector.css('a[data-testid="item-collection-card"], a[data-testid="category-card"]')
        for card in cards:
            name = card.css('div::text').get() or card.xpath('.//div/text()').get()
            url = card.attrib.get('href')
            if url and '/instamart/city/' in url:
                full_url = "https://www.swiggy.com" + url.split('?')[0]
                categories.append({"name": name, "url": full_url})

        # deduplicate
        unique_cats = {c['url']: c for c in categories if c['name']}.values()
        
        for cat in unique_cats:
            self.save_category({
                "category_name": cat['name'],
                "url": cat['url'],
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
        logger.info("Found %d main categories.", len(unique_cats))
        return [c['url'] for c in unique_cats]

    def fetch_subcategories(self, category_url):
        """Extract subcategories from a specific category page."""
        logger.info("Fetching subcategories for: %s", category_url)
        response = self._make_request(category_url, referer=settings.BASE_URL)
        if not response:
            return

        # Debug: Save HTML to inspect structure
        with open("debug_subcategory.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        logger.info("Saved HTML to debug_subcategory.html for inspection.")

        selector = Selector(text=response.text)
        count = 0
        
        # Extract Category Name from breadcrumb or title if possible
        category_name = selector.css('h1::text').get() or category_url.split('/')[-1].replace('-', ' ').title()

        # Swiggy Sidebar Subcategories
        # Try multiple selectors for robustness
        sub_items = selector.css('a[data-testid="subcategory-item"]')
        if not sub_items:
            # Fallback 1: Links containing "/sc/" in the href
            sub_items = selector.css('ul[class*="cxJLFr"] a[href*="/sc/"]')
        if not sub_items:
            # Fallback 2: General links containing "/sc/"
            sub_items = selector.css('a[href*="/sc/"]')
        
        seen_urls = set()
        
        for item in sub_items:
            name = item.css('div::text').get()
            url = item.attrib.get('href')
            
            if name and url:
                full_url = "https://www.swiggy.com" + url.split('?')[0]
                
                # Validation: Ensure it's under the instamart path and not a repeat
                if '/instamart/' in full_url and full_url not in seen_urls:
                    data = {
                        "main_category_name": category_name,
                        "subcategory_name": name,
                        "url": full_url,
                        "parent_url": category_url,
                        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.save_subcategory(data)
                    seen_urls.add(full_url)
                    count += 1
                    
        logger.info("Found %d subcategories for category '%s'.", count, category_name)

    def run(self, seed_urls=None):
        """Main execution flow with optional seed URLs."""
        if seed_urls:
            targets = seed_urls
            logger.info("Using provided seed URLs: %s", targets)
        else:
            targets = self.extract_main_categories()
            if not targets:
                logger.warning("No categories found from home page. Check selectors.")
                return

        for url in targets:
            # Random delay
            time.sleep(random.uniform(2, 5))
            try:
                self.fetch_subcategories(url)
            except Exception as e:
                logger.error("Error processing %s: %s", url, e)

        logger.info("Scraping finished.")

if __name__ == "__main__":
    # Example usage with specific category provided by user
    SEEDS = [
        "https://www.swiggy.com/instamart/city/bangalore/c/tea-coffee-and-more"
    ]
    scraper = SwiggyCategoryScraper()
    scraper.run(seed_urls=SEEDS)
