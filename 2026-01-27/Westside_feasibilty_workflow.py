
# =======================================
# Settings
# =======================================

HEADLESS = True
PAGE_TIMEOUT = 60000
SLOW_MO = 0   

OUTPUT_FILE = "westside_2026-01-27.csv"

HOME_CATEGORIES = {
    "Living": "https://www.westside.com/collections/living",
    "Kitchen": "https://www.westside.com/collections/kitchen",
    "Bed": "https://www.westside.com/collections/bed",
    "Bath": "https://www.westside.com/collections/bath",
}


# =======================================
# Category Extraction
# =======================================

class CategoryManager:

    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers

    def get_category_urls(self):
        response = requests.get(self.base_url, headers=self.headers)
        sel = Selector(text=response.text)

        # Xpath for Category Links
        category_links = sel.xpath(
            "//div[contains(@class,'list-menu-dropdown')]"
            "//div[contains(@class,'menu__dropdown-grandchild-container')]"
            "//li/a/@href"
        ).getall()

        return category_links


# ========================================
# PDP url Extraction - Crawler
# ========================================

from playwright.sync_api import sync_playwright


class WestsideCrawler:

    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=HEADLESS)
        self.context = self.browser.new_context()

    def open(self, url):
        page = self.context.new_page()
        page.goto(url, timeout=PAGE_TIMEOUT)
        return page

    def close(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()


# ========================================
# PDP field Extraction - parser
# ========================================

def run():

    crawler = WestsideCrawler()
    parser = WestsideParser()
    category_manager = CategoryManager()

    results = []

    for main_category, start_url in HOME_CATEGORIES.items():
        print(f"\n Crawling MAIN CATEGORY → {main_category}")

        breadcrumb = ["Home", main_category]

        end_categories = category_manager.crawl_categories(
            crawler=crawler,
            start_url=start_url,
            breadcrumb=breadcrumb
        )

        print(f" Found {len(end_categories)} end categories")

        for cat in end_categories:
            category_path = cat["breadcrumb"]
            category_url = cat["url"]

            main_cat = category_path[1] if len(category_path) > 1 else ""
            sub_cat = category_path[2] if len(category_path) > 2 else ""
            end_cat = category_path[-1]

            print(f" Scraping: {' > '.join(category_path)}")

            # -------- OPEN CATEGORY PAGE --------
            cat_page = crawler.open(category_url)
            cat_page.wait_for_timeout(4000)

            product_urls = parser.get_product_urls(cat_page)
            cat_page.close()

            print(f" Found {len(product_urls)} products")

            # -------- LOOP PRODUCTS --------
            for idx, product_url in enumerate(product_urls, start=1):
                print(f"   🔹 ({idx}/{len(product_urls)}) {product_url}")

                try:
                    product_page = crawler.open(product_url)
                    product_page.wait_for_timeout(3000)

                    product_json = parser.get_product_json(product_page)
                    details = parser.get_details(product_page)

                    results.append({
                        "main_category": main_cat,
                        "sub_category": sub_cat,
                        "end_category": end_cat,
                        "url": product_url,
                        "brand": product_json.get("brand", {}).get("name", ""),
                        "title": product_json.get("name", ""),
                        "selling_price": parser.get_price(product_json),
                        "sku": product_json.get("sku", ""),
                        "description": product_json.get("description", ""),
                        "net_quantity": details.get("net_quantity", ""),
                        "fit": details.get("fit", ""),
                        "care_instruction": details.get("care_instruction", ""),
                        "fabric_composition": details.get("fabric_composition", ""),
                        "country_of_origin": details.get("country_of_origin", "")
                    })

                    product_page.close()

                except Exception as e:
                    print("Error:", e)

    crawler.close()


##############################FINDINGS##############################

#1. Website Structure

# Westside uses collection-based URLs like
# /collections/living, /collections/kitchen, etc.
# Products are also available in multiple collection paths, which can lead to duplicate URLs.
# Categories are nested (Main → Sub → End Category).

#2. Navigation & Category Handling
# Category menus are loaded dynamically.
# Required Playwright browser automation instead of only requests.
# Breadcrumb structure helped identify hierarchy:
# Home > Main Category > Sub Category > End Category.


#  3. Pagination / Product Loading
# Westside uses Infinite Scroll instead of page numbers.
# Products load only when scrolling down.
# Static scraping (requests) was insufficient — needed Playwright scrolling logic.

Westside_feasibility_workflow.py
Displaying Westside_feasibility_workflow.py
