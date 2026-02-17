import logging
import time
import random
import json
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
        """Initialize MongoDB client and Session with impersonation."""
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]
        self.collection = self.db[settings.MONGO_COLLECTION_CATEGORY]
        
        # Create unique index to avoid duplicates at database level
        self.collection.create_index("url", unique=True)
        
        self.session = requests.Session()
        logger.info("Crawler initialized. Database: %s, Collection: %s", 
                    settings.MONGO_DB, settings.MONGO_COLLECTION_CATEGORY)

    def _make_request(self, url, referer=None, is_homepage=False):
        """
        Make a request with curl_cffi, including retries and exponential backoff.
        Uses manual bypass headers (cookies) provided by user as primary strategy.
        """
        attempts = 0
        while attempts < settings.RETRY_MAX_ATTEMPTS:
            try:
                # Use manual bypass headers for first 2 attempts, then fallback to auto rotation
                if attempts < 2:
                    impersonate, headers, cookies = settings.get_manual_config()
                    logger.debug("Attempt %d: Using Manual Bypass", attempts + 1)
                else:
                    impersonate, headers = settings.get_session_config(is_homepage=is_homepage)
                    cookies = None
                    logger.debug("Attempt %d: Using Automatic Rotation", attempts + 1)
                
                # Add/Update referer if needed
                if referer:
                    headers["Referer"] = referer
                elif is_homepage:
                    headers["Referer"] = settings.BASE_URL
                
                response = self.session.get(
                    url,
                    headers=headers,
                    cookies=cookies if attempts < 2 else None,
                    impersonate=impersonate,
                    timeout=settings.REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    # Successfully bypassed
                    return response
                
                if response.status_code in [403, 401, 429]:
                    logger.warning("Still Blocked (%s) for %s. Attempt %d/%d", 
                                   response.status_code, url, attempts + 1, settings.RETRY_MAX_ATTEMPTS)
                else:
                    logger.error("HTTP %s for %s", response.status_code, url)
                
            except Exception as e:
                logger.error("Request error for %s: %s", url, e)
            
            attempts += 1
            if attempts < settings.RETRY_MAX_ATTEMPTS:
                # Fallback to automatic rotation if manual fails repeatedly
                wait_time = (settings.RETRY_BACKOFF_FACTOR ** attempts) + random.uniform(5, 10)
                logger.info("Retry Triggered: Waiting %.2fs before next attempt", wait_time)
                time.sleep(wait_time)
            
        return None

    def save_to_db(self, data):
        """Save unique category information to MongoDB efficiently using upsert."""
        try:
            url = data.get("url")
            if not url:
                return
            
            self.collection.update_one(
                {"url": url},
                {"$set": data},
                upsert=True
            )
            logger.debug("Saved to DB: %s", url)
        except errors.PyMongoError as e:
            logger.error("Database save error: %s", e)

    def extract_main_categories(self):
        """Fetch homepage and extract main category links from the menu."""
        logger.info("Fetching homepage to extract main categories...")
        response = self._make_request(settings.BASE_URL, is_homepage=True)
        
        if not response:
            logger.critical("Failed to fetch homepage. Check your configuration/network.")
            return []

        selector = Selector(text=response.text)
        
        # BROAD SELECTORS for Worten Categories
        # Target main navigation menu items specifically if possible
        xpaths = [
            "//nav//a[contains(@class, 'main-nav')]/@href",
            "//div[contains(@id, 'menu')]//a/@href",
            "//a[contains(@class, 'category')]/@href",
            "//a[contains(@href, '/c/')]/@href", # Legacy pattern
            "//div[contains(@class, 'navigation')]//a/@href"
        ]
        
        category_links = []
        for xpath in xpaths:
            found = selector.xpath(xpath).getall()
            if found:
                category_links.extend(found)
        
        # Blacklist for non-category links
        blacklist = [
            'login', 'basket', 'conta', 'wishlist', 'carrinho', 'favoritos', 
            'ajuda', 'blog', 'contactos', 'campanha', 'promocoes', 'worten-life',
            'servicos', 'newsletter', 'cupoes', 'diretorio', 'novidades',
            'experiencias', 'hotjar', 'vouchers', 'encomendas', 'privacy', 'legal'
        ]

        # Basic cleanup: remove fragments, duplicates and normalize URLs
        clean_links = set()
        for link in category_links:
            # Filters
            if not link or len(link) < 3: continue
            if link.startswith(('#', 'javascript:', 'mailto:', 'tel:')): continue
            
            # Skip common non-category paths
            link_lower = link.lower()
            if any(x in link_lower for x in blacklist):
                continue
            
            # Category links are usually paths without extensions and not overly deep for main nav
            path_parts = [p for p in link.split('?')[0].strip('/').split('/') if p]
            if not path_parts or len(path_parts) > 2:
                # Main nav categories are usually top level or 1 level deep
                continue

            full_url = link if link.startswith("http") else settings.BASE_URL.rstrip('/') + '/' + link.lstrip('/')
            normalized_url = full_url.split("?")[0].rstrip("/")
            clean_links.add(normalized_url)
            
        # FALLBACK: If no links, try to extract from __NUXT_DATA__ script using regex
        if not clean_links:
            logger.warning("No categories found with standard selectors. Attempting NUXT_DATA extraction...")
            import re
            # Find all strings like "/abc-def" inside quotes (Safer regex to avoid backtracking)
            paths = re.findall(r'\"(/[a-z0-9-/]+)\"', response.text)
            for p in paths:
                p_lower = p.lower()
                if any(x in p_lower for x in blacklist): continue
                
                parts = [part for part in p.strip('/').split('/') if part]
                if 1 <= len(parts) <= 2:
                    full_url = settings.BASE_URL.rstrip('/') + '/' + p.lstrip('/')
                    clean_links.add(full_url.rstrip('/'))

        if not clean_links:
            logger.warning("Still no categories found. Saving HTML to debug_homepage.html")
            with open("debug_homepage.html", "w", encoding="utf-8") as f:
                f.write(response.text)

        logger.info("Extracted %d unique main categories.", len(clean_links))
        return list(clean_links)

    def fetch_subcategories(self, main_url):
        """Extract subcategories from a main category page."""
        name = main_url.split("/")[-1].replace("-", " ").title()
        logger.info("Processing Category: %s", name)
        
        response = self._make_request(main_url)
        if not response:
            logger.error("Could not fetch subcategories for %s", main_url)
            return

        selector = Selector(text=response.text)
        
        # Look for subcategory links in grids, menus, or sidebars
        # Target links that are likely part of the category hierarchy
        sub_xpaths = [
            "//a[contains(@class, 'category')]//@href",
            "//div[contains(@id, 'subcategory')]//a/@href",
            "//div[contains(@class, 'grid')]//a/@href",
            "//a[contains(@href, '/c/')]/@href", # Legacy
            "//div[contains(@class, 'navigation')]//a/@href"
        ]
        
        sub_links_found = []
        for xpath in sub_xpaths:
            links = selector.xpath(xpath).getall()
            if links:
                sub_links_found.extend(links)
                
        # If no specific containers, fallback to all links with names
        if not sub_links_found:
             sub_links_found = selector.xpath("//a").getall()

        blacklist = [
            'login', 'basket', 'conta', 'wishlist', 'carrinho', 'favoritos', 
            'ajuda', 'blog', 'contactos', 'campanha', 'promocoes', 'worten-life',
            'servicos', 'newsletter', 'cupoes', 'diretorio', 'novidades',
            'experiencias', 'hotjar', 'vouchers', 'encomendas', 'privacy', 'legal'
        ]

        count = 0
        seen_in_page = set()
        
        # In Nuxt apps, the data is often in the DOM as well
        for link_href in sub_links_found:
            if not link_href or len(link_href) < 3: continue
            if link_href.startswith(('#', 'javascript:', 'mailto:', 'tel:')): continue
            
            link_lower = link_href.lower()
            if any(x in link_lower for x in blacklist):
                continue
                
            full_sub_url = link_href if link_href.startswith("http") else settings.BASE_URL.rstrip('/') + '/' + link_href.lstrip('/')
            normalized_sub_url = full_sub_url.split("?")[0].rstrip("/")
            
            if normalized_sub_url == main_url or normalized_sub_url in seen_in_page:
                continue

            # Check if it looks like a subcategory (usually deeper than main_url or has /c/)
            # Or just accept everything that passed the blacklist and is not the main_url
            
            # Fetch name from the link text or an aria-label
            # Note: We'd need to re-find the element to get its text if we only have hrefs
            # Let's use a better loop
            pass # We'll re-implement the loop below

        # Better loop to get names
        for sub_el in selector.xpath("//a[@href]"):
            sub_url = sub_el.xpath("@href").get()
            sub_name = sub_el.xpath("normalize-space(.)").get() or sub_el.xpath("@aria-label").get() or sub_el.xpath("@title").get()
            
            if not sub_url or not sub_name or len(sub_name) < 2:
                continue
            
            sub_url_lower = sub_url.lower()
            if any(x in sub_url_lower for x in blacklist):
                continue
                
            full_sub_url = sub_url if sub_url.startswith("http") else settings.BASE_URL.rstrip('/') + '/' + sub_url.lstrip('/')
            normalized_sub_url = full_sub_url.split("?")[0].rstrip("/")
            
            if normalized_sub_url == main_url or normalized_sub_url in seen_in_page:
                continue
            
            # Only save if it looks like a related category/subcategory
            # Usually subcategories are deeper in the path or follow a similar slug
            main_slug = main_url.split('/')[-1]
            if main_slug in normalized_sub_url or "/c/" in sub_url:
                data = {
                    "main_category_name": name,
                    "subcategory_name": sub_name,
                    "url": normalized_sub_url,
                    "parent_url": main_url,
                    "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                self.save_to_db(data)
                seen_in_page.add(normalized_sub_url)
                count += 1
                
        logger.info("Found %d subcategories for %s", count, name)

    def run(self):
        """Main execution flow."""
        main_categories = self.extract_main_categories()
        
        if not main_categories:
            logger.warning("No main categories found. Ending run.")
            return

        # Limit to 20 categories per run for stability as per initial sample
        targets = main_categories[:20]
        logger.info("Starting subcategory extraction for %d targets...", len(targets))
        
        for url in targets:
            # Human-like delay
            delay = random.uniform(3, 7)
            logger.info("Waiting %.2fs before next category...", delay)
            time.sleep(delay)
            
            try:
                self.fetch_subcategories(url)
            except Exception as e:
                logger.error("Unhandled error in run loop for %s: %s", url, e)

        logger.info("Crawling completed successfully.")

if __name__ == "__main__":
    crawler = WortenCrawler()
    crawler.run()
