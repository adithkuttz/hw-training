import csv
import json
import time
from playwright.sync_api import sync_playwright

SEARCH_URL = "https://www.westside.com/search?q=shirt"
OUTPUT_FILE = "westside_products.csv"
MAX_PRODUCTS = 1000   # safety limit

FIELDS = [
    "url",
    "brand",
    "title",
    "selling_price",
    "sku",
    "description",
    "net_quantity",
    "fit",
    "care_instruction",
    "fabric_composition",
    "country_of_origin"
]

def scrape():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # ---------- SEARCH PAGE ----------
        page.goto(SEARCH_URL, timeout=60000)
        page.wait_for_selector('a[href*="/products/"]')

        product_urls = page.eval_on_selector_all(
            'a[href*="/products/"]',
            "els => [...new Set(els.map(e => e.href.split('?')[0]))]"
        )

        print(f"Found {len(product_urls)} product URLs")

        # ---------- PRODUCT PAGES ----------
        for url in product_urls[:MAX_PRODUCTS]:
            print("Scraping:", url)
            page.goto(url, timeout=60000)
            page.wait_for_timeout(2500)

            # ---------- JSON-LD ----------
            product_json = {}
            scripts = page.locator('script[type="application/ld+json"]').all()

            for s in scripts:
                try:
                    data = json.loads(s.inner_text())
                    if isinstance(data, dict) and data.get("@type") == "Product":
                        product_json = data
                        break
                except:
                    continue

            # ---------- PRICE ----------
            selling_price = "N/A"
            offers = product_json.get("offers")
            if isinstance(offers, dict):
                selling_price = offers.get("price", "N/A")
            elif isinstance(offers, list) and offers:
                selling_price = offers[0].get("price", "N/A")

            # ---------- DETAILS DEFAULTS ----------
            net_quantity = "1N"          # default (industry-safe)
            fit = "Regular Fit"          # default
            care_instruction = "N/A"
            fabric_composition = "N/A"
            country_of_origin = "India"  # default fallback

            # ---------- PRODUCT DETAILS BLOCK ----------
            try:
                details_text = page.locator(
                    "div:has-text('Product Details')"
                ).inner_text()

                lines = [l.strip() for l in details_text.split("\n") if ":" in l]

                for line in lines:
                    key, value = line.split(":", 1)
                    key = key.lower()

                    if "net quantity" in key:
                        net_quantity = value.strip()
                    elif "fit" in key:
                        fit = value.strip()
                    elif "care" in key:
                        care_instruction = value.strip()
                    elif "fabric" in key:
                        fabric_composition = value.strip()
                    elif "country" in key:
                        country_of_origin = value.strip()
            except:
                pass

            results.append({
                "url": url,
                "brand": product_json.get("brand", {}).get("name", "Westside"),
                "title": product_json.get("name", "N/A"),
                "selling_price": selling_price,
                "sku": product_json.get("sku", "N/A"),
                "description": product_json.get("description", "N/A"),
                "net_quantity": net_quantity,
                "fit": fit,
                "care_instruction": care_instruction,
                "fabric_composition": fabric_composition,
                "country_of_origin": country_of_origin
            })

            time.sleep(1)

        browser.close()

    # ---------- SAVE CSV ----------
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved {len(results)} products → {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape()
