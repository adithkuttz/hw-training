# main.py
import csv
import time

from crawler import WestsideCrawler
from westside_parser import WestsideParser
from westside_category import CategoryManager


FIELDS = [
    "main_category",
    "sub_category",
    "end_category",
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

HOME_CATEGORIES = {
    "Living": "https://www.westside.com/collections/living",
    "Kitchen": "https://www.westside.com/collections/kitchen",
    "Bed": "https://www.westside.com/collections/bed",
    "Bath": "https://www.westside.com/collections/bath",
}


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
                    print(f" Failed product: {product_url}")
                    try:
                        product_page.close()
                    except:
                        pass
                    continue

    crawler.close()

    
    with open("westside_home_categories.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)

    print("\n DONE — CSV saved as westside_home_categories.csv")


if __name__ == "__main__":
    run()
