import logging
import time
import random
import sys
from curl_cffi import requests
from parsel import Selector
from pymongo import MongoClient, errors
import worten_settings as settings

# ---------- LOGGING SETUP ----------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class WortenCrawler:
    def __init__(self):
        """Initialize MongoDB client and requests Session."""
        try:
            self.client = MongoClient(settings.MONGO_URI)
            self.db = self.client[settings.MONGO_DB]
            # Use subcategory collection as target for final outputs
            self.collection = self.db[settings.MONGO_COLLECTION_SUBCATEGORY]
            
            # Ensure unique index on URL
            self.collection.create_index("url", unique=True)
            
            self.session = requests.Session()
            logger.info("Crawler initialized. Database: %s, Target Collection: %s", 
                        settings.MONGO_DB, settings.MONGO_COLLECTION_SUBCATEGORY)
        except Exception as e:
            logger.critical("Failed to initialize crawler/database: %s", e)
            sys.exit(1)

    def _make_request(self, url, referer=None, is_homepage=False):
        """
        Execute request with retries and graceful error handling.
        Uses configuration (impersonation, headers, cookies) from settings.
        """
        attempts = 0
        while attempts < settings.RETRY_MAX_ATTEMPTS:
            try:
                # Use manual bypass configuration for initial attempts
                if attempts < 2:
                    impersonate, headers, cookies = settings.get_manual_config()
                else:
                    # Fallback to rotation logic if manual bypass fails
                    impersonate, headers = settings.get_session_config(is_homepage=is_homepage)
                    cookies = None
                
                # Dynamic headers update
                if referer:
                    headers["Referer"] = referer
                elif is_homepage:
                    headers["Referer"] = settings.BASE_URL

                response = self.session.get(
                    url,
                    headers=headers,
                    cookies=cookies if (attempts < 2 and cookies) else None,
                    impersonate=impersonate,
                    timeout=settings.REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response
                
                if response.status_code in [401, 403, 429]:
                    logger.warning("Bypass blocked (%d) for %s. Attempt %d/%d", 
                                   response.status_code, url, attempts + 1, settings.RETRY_MAX_ATTEMPTS)
                else:
                    logger.error("HTTP %d for %s", response.status_code, url)
                
            except Exception as e:
                logger.error("Request failed for %s: %s", url, e)
            
            attempts += 1
            if attempts < settings.RETRY_MAX_ATTEMPTS:
                backoff = (settings.RETRY_BACKOFF_FACTOR ** attempts) + random.uniform(2, 5)
                logger.info("Retrying in %.2fs...", backoff)
                time.sleep(backoff)
        
        return None

    def save_to_db(self, data):
        """Upsert document into MongoDB to prevent duplicates."""
        try:
            url = data.get("url")
            if not url: return
            
            self.collection.update_one(
                {"url": url},
                {"$set": data},
                upsert=True
            )
        except errors.PyMongoError as e:
            logger.error("Database save error: %s", e)

    def extract_main_categories(self):
        """Navigate to homepage and extract primary category links."""
        logger.info("Fetching homepage: %s", settings.BASE_URL)
        response = self._make_request(settings.BASE_URL, is_homepage=True)
        
        if not response:
            logger.critical("Failed to fetch homepage after all retries. Consider updating cookies.")
            return []

        selector = Selector(text=response.text)
        
        # Comprehensive selectors for categories
        xpaths = [
            "//nav//a[contains(@class, 'main-nav')]/@href",
            "//div[contains(@id, 'menu')]//a/@href",
            "//a[contains(@class, 'category')]/@href",
            "//a[contains(@href, '/c/')]/@href"
        ]
        
        links = set()
        for xpath in xpaths:
            found = selector.xpath(xpath).getall()
            for l in found:
                if not l or len(l) < 3: continue
                # Basic filter
                if any(x in l.lower() for x in ['login', 'basket', 'conta', 'ajuda', 'legal', 'privacy', 'blog']):
                    continue
                
                # Normalize
                full_url = l if l.startswith("http") else settings.BASE_URL.rstrip('/') + '/' + l.lstrip('/')
                links.add(full_url.split('?')[0].rstrip('/'))
        
        # Fallback to NUXT_DATA if empty
        if not links:
            import re
            paths = re.findall(r'\"(/[a-z0-9-/]+)\"', response.text)
            for p in paths:
                if any(x in p.lower() for x in ['login', 'basket', 'conta']): continue
                parts = [x for x in p.strip('/').split('/') if x]
                if 1 <= len(parts) <= 2:
                    full_url = settings.BASE_URL.rstrip('/') + '/' + p.lstrip('/')
                    links.add(full_url.rstrip('/'))

        logger.info("Extracted %d unique main categories", len(links))
        return list(links)

    def fetch_subcategories(self, main_url):
        """Process a main category page to find nested subcategories."""
        logger.info("Processing Category: %s", main_url)
        response = self._make_request(main_url, referer=settings.BASE_URL)
        
        if not response:
            logger.error("Could not fetch subcategories for %s", main_url)
            return

        selector = Selector(text=response.text)
        main_name = main_url.split('/')[-1].replace('-', ' ').title()
        
        count = 0
        seen_urls = {main_url}
        
        for el in selector.xpath("//a[@href]"):
            sub_url_raw = el.xpath("@href").get()
            sub_name = el.xpath("normalize-space(.)").get() or el.xpath("@aria-label").get()
            
            if not sub_url_raw or not sub_name or len(sub_name) < 2: continue
            
            # Filter
            if any(x in sub_url_raw.lower() for x in ['login', 'basket', 'conta', 'newsletter', 'wishlist']): continue
            
            full_sub_url = sub_url_raw if sub_url_raw.startswith("http") else settings.BASE_URL.rstrip('/') + '/' + sub_url_raw.lstrip('/')
            normalized_url = full_sub_url.split('?')[0].rstrip('/')
            
            if normalized_url in seen_urls: continue
            
            # Logic: Subcategories usually contain main slug or /c/
            main_slug = main_url.split('/')[-1]
            if main_slug in normalized_url or "/c/" in sub_url_raw:
                data = {
                    "main_category": main_name,
                    "subcategory_name": sub_name,
                    "url": normalized_url,
                    "parent_url": main_url,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                self.save_to_db(data)
                seen_urls.add(normalized_url)
                count += 1
        
        logger.info("  -> Saved %d subcategories for %s", count, main_name)

    def run(self):
        """Orchestrate the crawling flow."""
        main_categories = self.extract_main_categories()
        
        if not main_categories:
            logger.warning("No categories to process. Run aborted.")
            return

        # Limit run size for stability
        targets = main_categories[:20]
        logger.info("Starting subcategory crawl for %d targets...", len(targets))
        
        for url in targets:
            # Human-like browsing delay
            delay = random.uniform(3, 7)
            logger.info("Sleeping %.2fs before next page...", delay)
            time.sleep(delay)
            
            try:
                self.fetch_subcategories(url)
            except Exception as e:
                logger.error("Error processing %s: %s", url, e)

        logger.info("Crawler execution completed successfully.")

if __name__ == "__main__":
    crawler = WortenCrawler()
    crawler.run()
