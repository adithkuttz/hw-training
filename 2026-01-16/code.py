import requests
import re
import json
import logging
from datetime import datetime, timezone
from parsel import Selector
from pymongo import MongoClient

# ================= LOGGING =================
logging.basicConfig(
    filename="next_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ================= HEADERS =================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-GB,en;q=0.9",
}

# ================= CONFIG =================
PLP_URL = "https://www.next.co.uk/shop/gender-women-category-dresses-0?p=1"
CATEGORY_NAME = "Women's Dresses"
OUTPUT_JSON = "products.json"

# ================= MONGODB =================
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "next_scraper"
COLLECTION_NAME = "products"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ================= FUNCTIONS =================

def get_pdp_urls(plp_url):
    """Fetch PDP URLs from PLP page"""
    logging.info("Fetching PLP page")
    response = requests.get(plp_url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    sel = Selector(response.text)
    urls = sel.xpath("//a[contains(@href,'/style/')]/@href").getall()

    pdp_urls = []
    for url in urls:
        if not url.startswith("http"):
            url = "https://www.next.co.uk" + url
        pdp_urls.append(url)

    pdp_urls = list(set(pdp_urls))
    logging.info(f"PDP URLs found: {len(pdp_urls)}")
    return pdp_urls


def scrape_pdp(pdp_url):
    """Scrape data from PDP page"""
    try:
        logging.info(f"Scraping PDP: {pdp_url}")
        response = requests.get(pdp_url, headers=HEADERS, timeout=20)
        response.raise_for_status()

        sel = Selector(response.text)

        unique_id = re.findall(r"\d+", pdp_url)
        unique_id = unique_id[0] if unique_id else None

        product_name = sel.xpath("//h1/text()").get()

        selling_price = sel.xpath("//span[contains(text(),'£')]/text()").get()
        regular_price = sel.xpath("//del/text()").get()

        product_description = " ".join(
            sel.xpath("//div[contains(@class,'Description')]//text()").getall()
        ).strip()

        breadcrumb = " > ".join(
            sel.xpath("//nav//a/text()").getall()
        )

        images = sel.xpath("//img[contains(@src,'cdn.next.co.uk')]/@src").getall()

        data = {
            "unique_id": unique_id,
            "product_name": product_name,
            "brand": "Next",
            "category": CATEGORY_NAME,
            "regular_price": regular_price,
            "selling_price": selling_price,
            "currency": "GBP",
            "promotion_description": None,
            "breadcrumb": breadcrumb,
            "product_description": product_description,
            "color": None,
            "size": None,
            "rating": None,
            "review": None,
            "material_composition": None,
            "style": None,
            "care_instructions": None,
            "feature": None,
            "composition": None,
            "images": images,
            "pdp_url": pdp_url,
            "scraped_at": datetime.now(timezone.utc).isoformat()
        }

        return data

    except Exception as e:
        logging.error(f"PDP error {pdp_url} - {e}")
        return None


# ================= MAIN =================
def main():
    logging.info("Scraping started")

    products = []
    pdp_urls = get_pdp_urls(PLP_URL)

    for url in pdp_urls:
        product = scrape_pdp(url)
        if product:
            products.append(product)
            collection.update_one(
                {"unique_id": product["unique_id"]},
                {"$set": product},
                upsert=True
            )

    # Save JSON ARRAY
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    logging.info(f"Scraping completed. Products scraped: {len(products)}")
    print(f"Scraping completed. Products scraped: {len(products)}")


if __name__ == "__main__":
    main()
