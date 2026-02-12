import json
import logging
import time
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

# ---------------- CONFIG ---------------- #
BASE_URL = "https://www.lidl.co.uk"
OUTPUT_FILE = "lidl_categories.json"

# Keywords to exclude
EXCLUDE_KEYWORDS = [
    "privacy", "cookie", "legal", "compliance", "help", 
    "sign", "account", "app", "finder", "gift", "store-finder",
    "terms", "about", "contact"
]

# ---------------- LOGGING ---------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def is_valid_url(url):
    """Check if URL is valid and does not contain excluded keywords."""
    if not url:
        return False
    lower_url = url.lower()
    
    # Must contain /c/ or categoryId=
    if "/c/" not in lower_url and "categoryid=" not in lower_url:
        return False
        
    for keyword in EXCLUDE_KEYWORDS:
        if keyword in lower_url:
            return False
    return True

def scrape_lidl():
    data = []
    
    with sync_playwright() as p:
        # Launch browser - Headless=False to see what's happening (optional, can be True)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            logger.info("Navigating to Homepage: %s", BASE_URL)
            page.goto(BASE_URL, timeout=60000)
            
            # Handle Cookie Consent if present (Generic attempt)
            try:
                # Common selector for cookie acceptance - Adjust if needed
                page.click("button[data-testid='cookie-banner-accept-all-button']", timeout=5000)
                logger.info("Clicked Cookie Consent")
                time.sleep(1)
            except Exception:
                logger.info("No cookie banner found or could not click.")
            
            main_category_elements = page.query_selector_all("a[href*='/c/']")
            
            main_categories = []
            seen_main_urls = set()

            logger.info("Scanning for Main Categories...")
            
            # Filter for the "main" ones. Usually they are prominent.
            # We'll take unique valid URLs found in the top navigation area if possible.
            # Refinement: Look for elements that look like the main nav
            
            # Let's try to target the specific nav container if known, otherwise filter broad.
            # Assuming the "round icons" are the primary navigation.
            
            for el in main_category_elements:
                href = el.get_attribute("href")
                text = el.inner_text().strip()
                
                if not href:
                    continue
                    
                full_url = urljoin(BASE_URL, href)
                
                if not is_valid_url(full_url):
                    continue
                    
                if full_url in seen_main_urls:
                    continue

                # Heuristic: Main categories usually have short text or specific classes
                # For now, collect them. We might collect too many, but the validation logic helps.
                # To be more precise, we should assume the user wants the TOP level ones.
                
                # Check if it's strictly a category link
                seen_main_urls.add(full_url)
                main_categories.append({"name": text, "url": full_url})
                
            logger.info("Found %d potential Main Categories", len(main_categories))
            
            # ---------------- SUB CATEGORIES ---------------- #
            for main_cat in main_categories:
                main_name = main_cat['name']
                main_url = main_cat['url']
                
                logger.info("Scraping Sub Categories for: %s (%s)", main_name, main_url)
                
                try:
                    category_page = context.new_page()
                    category_page.goto(main_url, timeout=30000)
                  
                    
                    # Wait a bit for dynamic content
                    category_page.wait_for_load_state("domcontentloaded")
                    time.sleep(2) # brief wait for JS rendering
      
                    
                    sub_elements = category_page.query_selector_all("a[href*='/c/']")
                    
          
                    
                    found_subs = 0
                    seen_sub_urls = set()
                    
                    for sub_el in sub_elements:
                        sub_href = sub_el.get_attribute("href")
                        sub_text = sub_el.inner_text().strip()
                        
                        if not sub_href:
                            continue
                            
                        sub_full_url = urljoin(BASE_URL, sub_href)
                        
                        if not is_valid_url(sub_full_url):
                            continue
                            
                        if sub_full_url == main_url: # Skip self
                            continue
                            
                        if sub_full_url in seen_sub_urls:
                            continue
                        
                        # Heuristic: "Chips" often have no line breaks and are short.
                        # Also, check if it is "under In store offers" - we can't easily check visual position without bounding box,
                        # but we can rely on URL structure or DOM order.
                        
                        # Limit: If we found > 0, great.
                        # We will verify the output.
                        
                        seen_sub_urls.add(sub_full_url)
                        
                        data.append({
                            "main_name": main_name,
                            "main_url": main_url,
                            "sub_name": sub_text,
                            "sub_url": sub_full_url
                        })
                        found_subs += 1
                        
                    logger.info("  -> Found %d sub categories", found_subs)
                    category_page.close()
                    
                except Exception as e:
                    logger.error("Failed to scrape category %s: %s", main_name, e)
                    if 'category_page' in locals():
                        category_page.close()

        except Exception as e:
            logger.error("Scraper failed: %s", e)
        finally:
            browser.close()
            
    # Save to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info("Scraping complete. Data saved to %s", OUTPUT_FILE)

if __name__ == "__main__":
    scrape_lidl()
