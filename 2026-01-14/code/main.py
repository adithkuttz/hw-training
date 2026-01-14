import requests
from bs4 import BeautifulSoup

from settings import BASE_URL, RAW_HTML_FILE, CLEANED_DATA_FILE, HEADERS

class DataMiningError(Exception):
    """Custom exception for data mining errors"""
    pass


class CleverlebenParser:
    """Parser for Cleverleben product selection page"""

    def __init__(self):
        """Initialize basic requirements"""
        self.url = BASE_URL
        self.html = ""
        self.products = []

    def start(self):
        """Start crawling process"""
        print(f"[INFO] Starting crawl for {self.url}")
        self.fetch_html()
        self.parse_data()
        self.save_to_file()

    def fetch_html(self):
        """Fetch HTML using requests (Task 4: exception handling)"""
        try:
            response = requests.get(self.url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            self.html = response.text

            with open(RAW_HTML_FILE, "w", encoding="utf-8") as file:
                file.write(self.html)

            print("[SUCCESS] HTML fetched and saved")

        except requests.exceptions.RequestException as exc:
            print(f"[ERROR] Connection issue: {exc}")
            raise

    def parse_data(self):
        """Mock parsing for training task"""
        self.products = [
            {"name": "Basenpulver", "price": None},
            {"name": "Magnesium Kapseln", "price": None},
            {"name": "Vitamin D3 Tropfen", "price": None},
        ]

        print(f"[SUCCESS] Mock parsed {len(self.products)} products")


    def save_to_file(self):
        """Save cleaned data to text file"""
        with open(CLEANED_DATA_FILE, "w", encoding="utf-8") as file:
            for product in self.products:
                file.write(f"{product['name']}\n")

        print("[SUCCESS] Cleaned data saved")

    def yield_lines_from_file(self, filename):
        """Generator to read file line-by-line (Task 3)"""
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                yield line.strip()

    def close(self):
        """Close connections (Destructor logic)"""
        print("[INFO] Closing parser")

def filter_product_names(products):
    """Extract product names & remove null prices"""
    return [
        product["name"]
        for product in products
        if product["price"] is None
    ]


if __name__ == "__main__":
    parser = CleverlebenParser()

    try:
        parser.start()

        print("\n[INFO] Reading cleaned data using generator:")
        for line in parser.yield_lines_from_file(CLEANED_DATA_FILE):
            print(f"- {line}")

        filtered = filter_product_names(parser.products)
        print(f"\n[INFO] Filtered products count: {len(filtered)}")

    finally:
        parser.close()



