import csv
import re
import os
from html import unescape
from pymongo import MongoClient
import worten_settings as settings

# Define headers based on Worten project fields
csv_headers = [
    "unique_id", "url", "productname", "brand", "selling_price",
    "regular_price", "description", "specification", "image", 
    "rating", "review", "colour", "main_category", 
    "subcategory_name", "parent_url", "timestamp"
]

class Exporter:
    def __init__(self, writer):
        self.writer = writer
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]
        self.collection = self.db[settings.MONGO_COLLECTION_PRODUCT]

    def clean_text(self, text):
        """Clean HTML tags and normalize whitespace."""
        if not text:
            return ""
        text = str(text)
        # Remove HTML tags
        text = re.sub(r"<.*?>", " ", unescape(text))
        # Normalize whitespace (replace newlines/tabs with space, strip results)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def start(self):
        print(f"Starting export. Total products in DB: {self.collection.count_documents({})}")
        self.writer.writerow(csv_headers)
        
        count = 0
        for item in self.collection.find():
            row = []
            for h in csv_headers:
                val = item.get(h, "")
                
                # Apply cleaning to specific fields or all text fields
                if h in ["productname", "brand", "description", "specification", "colour", "main_category", "subcategory_name"]:
                    val = self.clean_text(val)
                elif val:
                    val = str(val).strip()
                
                row.append(val)
            
            self.writer.writerow(row)
            count += 1
            if count % 10 == 0:
                print(f"Exported {count} products...")

        print(f"Export finished. Total exported: {count}")

if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), settings.FILE_NAME_FULLDUMP)
    print(f"Exporting to: {path}")
    
    try:
        with open(path, "w", encoding="utf-8", newline="") as f:
            Exporter(csv.writer(f, quoting=csv.QUOTE_MINIMAL)).start()
        print("Export successful.")
    except Exception as e:
        print(f"Export failed: {e}")
