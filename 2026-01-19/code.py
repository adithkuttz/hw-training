import requests
import re
import json
import time
from urllib.parse import urljoin, urlparse
from parsel import Selector

# ---------------- CONFIG ----------------
BASE_URL = "https://www.cleverleben.at"
START_URL = "https://www.cleverleben.at/produktauswahl"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

MAX_PRODUCTS = 30          # 🔴 keep small
REQUEST_DELAY = 1          # polite delay

products = []
seen_urls = set()
STOP_CRAWL = False         # 🔴 global stop flag

# ---------------- SESSION (IMPORTANT) ----------------
session = requests.Session()
session.headers.update(HEADERS)

# ---------------- HELPERS ----------------
def clean_text(text):
    if not text:
        return None
    return re.sub(r"\s+", " ", text).strip()


def get_page(url):
    response = session.get(url, timeout=15)
    response.raise_for_status()
    return Selector(text=response.text)


# ---------------- STEP 1: CATEGORIES ----------------
def get_categories():
    sel = get_page(START_URL)
    links = sel.css("a::attr(href)").getall()

    categories = []
    for link in links:
        if link and link.startswith("/") and any(x in link for x in [
            "lebensmittel",
            "getraenke",
            "haushalt",
            "tier"
        ]):
            categories.append(urljoin(BASE_URL, link))

    categories = list(set(categories))
    print("CATEGORIES FOUND:", len(categories))
    return categories


# ---------------- STEP 2: SUB-CATEGORIES ----------------
def get_subcategories(category_url):
    sel = get_page(category_url)
    links = sel.css("a::attr(href)").getall()

    subcategories = []
    for link in links:
        if link and link.startswith("/produkte/"):
            subcategories.append(urljoin(BASE_URL, link))

    return list(set(subcategories))


# ---------------- STEP 3: PRODUCT LINKS ----------------
def get_product_links(subcategory_url):
    sel = get_page(subcategory_url)
    links = sel.css("a::attr(href)").getall()

    product_links = []
    for link in links:
        if link and "/produkt/" in link:
            product_links.append(urljoin(BASE_URL, link))

    return list(set(product_links))


# ---------------- STEP 4: PRODUCT PAGE ----------------
def parse_product(url):
    global STOP_CRAWL

    if STOP_CRAWL or url in seen_urls:
        return

    if len(products) >= MAX_PRODUCTS:
        STOP_CRAWL = True
        return

    seen_urls.add(url)
    sel = get_page(url)

    product = {}
    product["product_url"] = url
    product["product_name"] = clean_text(sel.xpath("//h1/text()").get())

    price_text = sel.xpath('//*[contains(text(), "€")][1]/text()').get()
    product["price"] = clean_text(price_text)
    product["currency"] = "€" if price_text else None

    if price_text:
        m = re.search(r"([\d,.]+)", price_text)
        product["regular_price"] = m.group(1).replace(",", ".") if m else None

    product["product_description"] = clean_text(
        sel.xpath("//h1/following::p[1]/text()").get()
    )

    pid_text = sel.xpath('//text()[contains(., "Produkt ID:")]').get()
    if pid_text:
        m = re.search(r"Produkt ID:\s*([A-Za-z0-9\-]+)", pid_text)
        product["product_id"] = m.group(1) if m else None

    m = re.search(r"(\d+)$", urlparse(url).path)
    product["unique_id"] = m.group(1) if m else None

    product["ingredients"] = clean_text(
        sel.xpath('//text()[starts-with(normalize-space(), "Zutaten:")]').get()
    )

    images = sel.xpath('//meta[@property="og:image"]/@content').getall()
    product["images"] = images
    product["image"] = images[0] if images else None

    products.append(product)
    print(f"[{len(products)}] Scraped:", product["product_name"])

    time.sleep(REQUEST_DELAY)


# ---------------- MAIN (FINAL SAFE FLOW) ----------------
def main():
    global STOP_CRAWL

    categories = get_categories()

    for category_url in categories:
        if STOP_CRAWL:
            break

        subcategories = get_subcategories(category_url)

        for subcategory_url in subcategories:
            if STOP_CRAWL:
                break

            product_links = get_product_links(subcategory_url)

            if not product_links:
                continue

            for product_url in product_links:
                parse_product(product_url)

                if STOP_CRAWL:
                    break

    with open("clever_products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"\n✅ DONE. Saved {len(products)} products safely.")


if __name__ == "__main__":
    main()
