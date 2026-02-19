import logging
import time
import random
import sys
import re
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

class WortenParser:
    def __init__(self):
        """Initialize MongoDB client and requests Session."""
        try:
            self.client = MongoClient(settings.MONGO_URI)
            self.db = self.client[settings.MONGO_DB]
            # Collection for product URLs to process (from crawler)
            self.subcat_collection = self.db[settings.MONGO_COLLECTION_SUBCATEGORY]
            # Target collection for extracted products
            self.product_collection = self.db[settings.MONGO_COLLECTION_PRODUCT]
            
            # Ensure unique indices
            self.product_collection.create_index("url", unique=True)
            self.product_collection.create_index("unique_id", unique=True)
            
            self.session = requests.Session()
            logger.info("Parser initialized. Database: %s, Product Collection: %s", 
                        settings.MONGO_DB, settings.MONGO_COLLECTION_PRODUCT)
        except Exception as e:
            logger.critical("Failed to initialize parser/database: %s", e)
            sys.exit(1)

    def _make_request(self, url, referer=None, is_homepage=False):
        """Execute request with retries and bypass logic."""
        attempts = 0
        while attempts < settings.RETRY_MAX_ATTEMPTS:
            try:
                if attempts < 2:
                    impersonate, headers, cookies = settings.get_manual_config()
                else:
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
                
                if response.status_code == 404:
                    logger.error("HTTP 404 (Not Found) for %s. Skipping.", url)
                    return response

                if response.status_code in [401, 403, 429]:
                    logger.warning("Bypass blocked (%d) for %s. Attempt %d/%d", 
                                   response.status_code, url, attempts + 1, settings.RETRY_MAX_ATTEMPTS)
                    if response.text and "Just a moment..." in response.text:
                        with open("debug_error.html", "w", encoding="utf-8") as f:
                            f.write(response.text)
                        logger.info("Saved blocked response to debug_error.html")
                else:
                    logger.error("HTTP %d for %s", response.status_code, url)


                
            except Exception as e:
                logger.error("Request failed for %s: %s", url, e)
            
            attempts += 1
            if attempts < settings.RETRY_MAX_ATTEMPTS:
                backoff = (settings.RETRY_BACKOFF_FACTOR ** attempts) + random.uniform(2, 5)
                time.sleep(backoff)
        
        return None

    def get_product_urls(self, plp_base_url):
        """Extract all product URLs from all pages of a subcategory (PLP)."""
        all_links = set()
        page = 1
        
        while True:
            # Build paginated URL (Worten usually uses ?page=X or similar)
            plp_url = f"{plp_base_url}?page={page}" if page > 1 else plp_base_url
            logger.info("Fetching PLP Page %d: %s", page, plp_url)
            
            response = self._make_request(plp_url, referer=settings.BASE_URL)
            if not response: break

            selector = Selector(text=response.text)
            links = set()
            
            # 1. Standard XPaths for product links
            product_xpaths = [
                "//a[contains(@href, '/produtos/')]/@href",
                "//a[contains(@href, '/p/')]/@href",
                "//a[contains(@class, 'product-card')]/@href",
                "//a[contains(@class, 'w-product__url')]/@href"
            ]
            
            for xpath in product_xpaths:
                found = selector.xpath(xpath).getall()
                for l in found:
                    if not l: continue
                    if '/produtos/' in l or '/p/' in l:
                        full_url = l if l.startswith("http") else settings.BASE_URL.rstrip('/') + '/' + l.lstrip('/')
                        links.add(full_url.split('?')[0].rstrip('/'))
            
            # 2. Regex Fallback
            if not links:
                paths = re.findall(r'\"(/[a-z0-9-/]*(?:produtos|/p/)[a-z0-9-/]+)\"', response.text)
                for p in paths:
                    if any(x in p.lower() for x in ['login', 'basket', 'conta']): continue
                    full_url = settings.BASE_URL.rstrip('/') + '/' + p.lstrip('/')
                    links.add(full_url.split('?')[0].rstrip('/'))

            if not links:
                logger.info("No more products found on page %d. Stopping pagination.", page)
                break
                
            logger.info("Found %d products on page %d", len(links), page)
            all_links.update(links)
            
            # Check if there's a 'next' page link to continue
            # Common Next page XPaths
            has_next = selector.xpath("//a[contains(@class, 'next')]|//link[@rel='next']").get()
            if not has_next and page >= 1: # Fallback: if we found products, try next page anyway up to a limit
                # If we found links, we'll try at least the next page
                if page > 5: 
                     break
            
            page += 1
            time.sleep(random.uniform(2, 4))
            
        logger.info("Total products found for subcategory: %d", len(all_links))
        return list(all_links)

    def parse_product_details(self, pdp_url, category_context=None):
        """Extract product details from a Product Detail Page (PDP)."""
        logger.info("Parsing PDP: %s", pdp_url)
        response = self._make_request(pdp_url, referer=settings.BASE_URL)
        if not response: return None

        selector = Selector(text=response.text)
        data = {
            "url": pdp_url,
            "productname": "",
            "selling_price": "",
            "regular_price": "",
            "brand": "",
            "rating": "",
            "review": "",
            "description": "",
            "specification": "",
            "image": "",
            "colour": ""
        }
        
        try:
            # Generate a truly unique ID using the slug or hash to avoid collisions (e.g., 'euros')
            slug_parts = [p for p in pdp_url.split('/') if p][-1].split('-')
            # Use last 2 parts if available to be more descriptive but unique
            data["unique_id"] = "-".join(slug_parts[-2:]) if len(slug_parts) >= 2 else slug_parts[-1]
            
            data["productname"] = (selector.xpath("//h1/text()").get() or 
                                 selector.xpath("//h1//span/text()").get() or 
                                 selector.xpath("//h1[contains(@class, 'title')]/text()").get() or
                                 selector.xpath("//title/text()").get() or "").strip()
            
            # Price extraction - try multiple patterns and clean up
            price_selectors = [
                 "//span[contains(@class, 'w-product__price__current')]/text()",
                 "//span[contains(@class, 'price')]//text()",
                 "//div[contains(@class, 'current-price')]//text()",
            ]
            for ps in price_selectors:
                price_text = selector.xpath(ps).getall()
                if price_text:
                    # Filter for currency symbol or numbers to avoid grabbing "Desde" or "Como funciona"
                    clean_price = "".join([t.strip() for t in price_text if '€' in t or any(c.isdigit() for c in t)])
                    if clean_price:
                        data["selling_price"] = clean_price
                        break
            
            old_price = selector.xpath("//span[contains(@class, 'w-product__price__old')]//text()|//span[contains(@class, 'old')]//text()|//span[contains(@class, 'regular-price')]//text()").getall()
            if old_price:
                data["regular_price"] = "".join([t.strip() for t in old_price if '€' in t or any(c.isdigit() for c in t)])
            
            # Brand extraction - check common locations
            data["brand"] = (selector.xpath("//a[contains(@class, 'brand')]//text()").get() or 
                           selector.xpath("//span[contains(@class, 'brand')]//text()").get() or
                           selector.xpath("//a[contains(@href, 'marca')]//text()").get() or
                           selector.xpath("//td[contains(text(), 'Marca')]/following-sibling::td/text()").get() or "").strip()
            
            data["rating"] = (selector.xpath("//span[contains(@class, 'rating')]//text()").get() or 
                            selector.xpath("//div[contains(@class, 'stars')]//@data-rating").get() or "").strip()
            
            review_text = selector.xpath("//span[contains(text(), 'avalia')]//text()").get()
            data["review"] = review_text.strip() if review_text else ""
            
            desc = selector.xpath("//div[contains(@id, 'description')]//text()|//div[contains(@class, 'about')]//text()|//div[contains(@class, 'details')]//text()").getall()
            data["description"] = " ".join([d.strip() for d in desc if d.strip()]).strip()
            
            specs = selector.xpath("//table//text()|//div[contains(@class, 'specifications')]//text()|//ul[contains(@class, 'specs')]//text()").getall()
            data["specification"] = " ".join([s.strip() for s in specs if s.strip()]).strip()
            
            # Image extraction
            data["image"] = (selector.xpath("//img[contains(@class, 'product-image')]//@src").get() or 
                           selector.xpath("//meta[@property='og:image']//@content").get() or 
                           selector.xpath("//div[contains(@class, 'gallery')]//img/@src").get() or "").strip()
            
            # Colour extraction - look for specific labels
            data["colour"] = (selector.xpath("//*[contains(text(), 'Cor')]/following::span[1]/text()").get() or 
                            selector.xpath("//span[contains(text(), 'Cor')]/following-sibling::span/text()").get() or
                            selector.xpath("//td[contains(text(), 'Cor')]/following-sibling::td/text()").get() or "").strip()
            
            if category_context:
                data.update(category_context)
            
            data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Final cleanup: ensure no nulls in data values
            for key in data:
                if data[key] is None:
                    data[key] = ""
            
            return data

            
        except Exception as e:
            logger.error("Error parsing %s: %s", pdp_url, e)
            return None

    def save_product(self, data):
        """Upsert product data into MongoDB."""
        try:
            if not data or not data.get("url"): 
                logger.warning("Empty data or missing URL. Not saving.")
                return
            
            self.product_collection.update_one(
                {"url": data["url"]},
                {"$set": data},
                upsert=True
            )
            # Use 'or' to ensure we log the URL if productname is None
            logger.info("Saved product: %s", data.get("productname") or data["url"])
        except errors.DuplicateKeyError as e:
            # If unique_id still fails, append a timestamp or use URL as fallback
            logger.warning("Duplicate ID collision for %s. Retrying with fallback ID.", data["url"])
            data["unique_id"] = f"{data['unique_id']}-{int(time.time())}"
            self.save_product(data)
        except errors.PyMongoError as e:
            logger.error("Database save error: %s", e)


    def run(self, total_limit=100):
        """Run the parser on subcategories until the total limit is reached."""
        subcategories = list(self.subcat_collection.find())
        logger.info("Starting product extraction for %d subcategories (Limit: %d products)", 
                    len(subcategories), total_limit)
        
        product_count = 0
        
        for sub in subcategories:
            if product_count >= total_limit:
                break
                
            subcat_url = sub.get("url")
            context = {
                "main_category": sub.get("main_category"),
                "subcategory_name": sub.get("subcategory_name"),
                "parent_url": sub.get("parent_url")
            }
            
            logger.info("Processing Subcategory: %s (%s)", context["subcategory_name"], subcat_url)
            product_urls = self.get_product_urls(subcat_url)
            
            for p_url in product_urls:
                if product_count >= total_limit:
                    logger.info("Reached total limit of %d products. Stopping.", total_limit)
                    break
                    
                # Random delay between products to be human-like
                time.sleep(random.uniform(3, 6))
                
                try:
                    product_data = self.parse_product_details(p_url, context)
                    if product_data:
                        self.save_product(product_data)
                        product_count += 1
                    else:
                        logger.error("Failed to parse details for %s", p_url)
                except Exception as e:
                    logger.error("Unexpected error for %s: %s", p_url, e)

        logger.info("Extraction completed. Total products saved: %d", product_count)

if __name__ == "__main__":
    parser = WortenParser()
    # Now running with a limit of 100 products as requested
    parser.run(total_limit=100)


