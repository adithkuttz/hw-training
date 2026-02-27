import csv
import re
import os
from html import unescape
from pymongo import MongoClient
import swiggy_settings as settings

# Define headers based on Swiggy project fields
csv_headers = [
    "unique_id", "url", "competitor_product_key", "product_unique_key",
    "product_name", "brand", "product_description", "breadcrumb",
    "producthierarchy_level1", "producthierarchy_level2", "producthierarchy_level3",
    "regular_price", "selling_price", "percentage_discount", "currency",
    "grammage_quantity", "grammage_unit", "ingredients", "nutritions",
    "nutritional_information", "instructions", "instructionforuse",
    "country_of_origin", "image_url_1", "instock", "last_updated"
]

class Exporter:
    def __init__(self, writer):
        self.writer = writer
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]
        self.collection = self.db[settings.MONGO_COLLECTION_PRODUCT_DETAILS]

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
        total_docs = self.collection.count_documents({})
        print(f"Starting export. Total products in DB: {total_docs}")
        self.writer.writerow(csv_headers)
        
        count = 0
        for item in self.collection.find():
            row = []
            for h in csv_headers:
                val = item.get(h, "")
                
                # Apply cleaning to text-heavy fields
                text_fields = [
                    "product_name", "brand", "product_description", "breadcrumb",
                    "producthierarchy_level1", "producthierarchy_level2", "producthierarchy_level3",
                    "ingredients", "nutritions", "nutritional_information", 
                    "instructions", "instructionforuse", "country_of_origin"
                ]
                
                if h in text_fields:
                    val = self.clean_text(val)
                elif val is not None:
                    val = str(val).strip()
                else:
                    val = ""
                
                row.append(val)
            
            self.writer.writerow(row)
            count += 1
            if count % 10 == 0:
                print(f"Exported {count} products...")

        print(f"Export finished. Total exported: {count}")

if __name__ == "__main__":
    # Ensure the export directory exists or use the current directory
    filename = settings.FILE_NAME_FULLDUMP
    path = os.path.join(os.path.dirname(__file__), filename)
    print(f"Exporting to: {path}")
    
    try:
        with open(path, "w", encoding="utf-8", newline="") as f:
            Exporter(csv.writer(f, quoting=csv.QUOTE_MINIMAL)).start()
        print("Export successful.")
    except Exception as e:
        print(f"Export failed: {e}")
