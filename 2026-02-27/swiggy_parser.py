import json
import re
import hashlib
import logging
from parsel import Selector
import swiggy_settings as settings

logger = logging.getLogger(__name__)

class SwiggyParser:
    @staticmethod
    def extract_data(html_content, url):
        """Extract product data from Swiggy PDP HTML."""
        data = {
            "unique_id": "",
            "competitor_product_key": "",
            "product_unique_key": "",
            "url": url,
            "breadcrumb": "",
            "producthierarchy_level1": "",
            "producthierarchy_level2": "",
            "producthierarchy_level3": "",
            "product_name": "",
            "brand": "",
            "grammage_quantity": "",
            "grammage_unit": "",
            "regular_price": "",
            "selling_price": "",
            "percentage_discount": "",
            "currency": "INR",
            "product_description": "",
            "ingredients": "",
            "nutritions": "",
            "nutritional_information": "",
            "instructions": "",
            "instructionforuse": "",
            "country_of_origin": "",
            "image_url_1": "",
            "instock": ""
        }

        # Unique ID based on URL
        data["unique_id"] = hashlib.sha256(url.encode()).hexdigest()

        # Extract Item ID from URL
        item_id_match = re.search(r'-([A-Z0-9]{10,})$', url.split('?')[0])
        if item_id_match:
            data["competitor_product_key"] = item_id_match.group(1)
            data["product_unique_key"] = item_id_match.group(1)

        # 1. Try to find ___INITIAL_STATE___
        state_match = re.search(r'window\.___INITIAL_STATE___\s*=\s*({.*?});', html_content, re.DOTALL)
        if state_match:
            try:
                state_json = json.loads(state_match.group(1))
                SwiggyParser._parse_state(state_json, data)
            except Exception as e:
                logger.error(f"Error parsing ___INITIAL_STATE___: {e}")

        # 2. Try to find __NEXT_DATA__
        if not data["product_name"]:
            next_data_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content, re.DOTALL)
            if next_data_match:
                try:
                    next_json = json.loads(next_data_match.group(1))
                    SwiggyParser._parse_next_data(next_json, data)
                except Exception as e:
                    logger.error(f"Error parsing __NEXT_DATA__: {e}")

        # 3. CSS/XPath Fallback for remaining fields
        selector = Selector(text=html_content)
        SwiggyParser._parse_html(selector, data)

        # Post-processing
        SwiggyParser._calculate_discount(data)
        SwiggyParser._clean_data(data)

        return data

    @staticmethod
    def _parse_state(state, data):
        """Parse data from window.___INITIAL_STATE___."""
        # Swiggy structure is nested. We need to find the product info.
        # Based on browser research: categoryListingV2.data.cardsData...
        # But on a direct PDP, it might be different. Let's look for item objects.
        
        def find_item_in_obj(obj):
            if isinstance(obj, dict):
                if "displayName" in obj and "brand" in obj and "variations" in obj:
                    return obj
                for v in obj.values():
                    res = find_item_in_obj(v)
                    if res: return res
            elif isinstance(obj, list):
                for v in obj:
                    res = find_item_in_obj(v)
                    if res: return res
            return None

        item = find_item_in_obj(state)
        if item:
            data["product_name"] = item.get("displayName")
            data["brand"] = item.get("brand")
            
            # Variations
            variations = item.get("variations", [])
            if variations:
                v = variations[0]
                data["regular_price"] = v.get("price", {}).get("mrp", {}).get("units")
                data["selling_price"] = v.get("price", {}).get("offerPrice", {}).get("units")
                data["product_description"] = v.get("shortDescription")
                data["instock"] = v.get("inventory", {}).get("inStock")
                
                # Image
                image_ids = v.get("imageIds", [])
                if image_ids:
                    data["image_url_1"] = f"https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/{image_ids[0]}"
                
                # Grammage
                qty_desc = v.get("quantityDescription", "")
                qty_match = re.search(r'([\d\.]+)\s*([a-zA-Z]+)', qty_desc)
                if qty_match:
                    data["grammage_quantity"] = qty_match.group(1)
                    data["grammage_unit"] = qty_match.group(2)

            # Hierarchy / Breadcrumb
            levels = []
            if item.get("superCategory"): levels.append(item.get("superCategory"))
            if item.get("subCategoryType"): levels.append(item.get("subCategoryType"))
            
            if levels:
                data["breadcrumb"] = " > ".join(levels)
                data["producthierarchy_level1"] = levels[0] if len(levels) > 0 else None
                data["producthierarchy_level2"] = levels[1] if len(levels) > 1 else None
                data["producthierarchy_level3"] = levels[2] if len(levels) > 2 else None

    @staticmethod
    def _parse_next_data(next_data, data):
        """Parse data from __NEXT_DATA__."""
        # Similar logic to _parse_state if needed. 
        # Often Swiggy puts the same state in both or one of them.
        pass

    @staticmethod
    def _parse_html(selector, data):
        """Fallback CSS extraction and text-based search."""
        if not data["product_name"]:
            data["product_name"] = selector.css('h1::text').get()
        
        if not data["brand"]:
            data["brand"] = selector.css('div[class*="BrandName"]::text').get() or \
                           selector.xpath('//div[contains(text(), "Explore all products from")]/following-sibling::div/text()').get() or \
                           selector.css('a[href*="/brand/"]::text').get()

        if not data["product_description"]:
            # Description is often in multiple p tags or specific divs
            desc_parts = selector.css('div[id="ProductDescription"] p::text').getall() or \
                         selector.css('div[class*="Description"] p::text').getall()
            if desc_parts:
                data["product_description"] = "\n".join(desc_parts)

        # Robust text search for specific fields
        all_text = " ".join(selector.css('body *::text').getall())
        
        # Ingredients extraction
        if not data["ingredients"]:
            # Try CSS first
            data["ingredients"] = selector.xpath('//div[contains(text(), "Ingredients")]/following-sibling::div//p/text()').get() or \
                                selector.xpath('//div[contains(text(), "Ingredients")]/following-sibling::div/text()').get()
            
            if not data["ingredients"]:
                ing_match = re.search(r'Ingredients\s*:?\s*(.*?)(?:\s*(?:Nutritional|Manufacturer|Country|Seller)|$)', all_text, re.IGNORECASE | re.DOTALL)
                if ing_match:
                    data["ingredients"] = ing_match.group(1).strip(": ")

        # Country of Origin extraction
        if not data["country_of_origin"]:
            origin_match = re.search(r'Country Of Origin\s*:\s*([^.\n]+)', all_text, re.IGNORECASE)
            if origin_match:
                data["country_of_origin"] = origin_match.group(1).strip()

        # Nutritional Information / Nutritions
        if not data["nutritions"]:
            data["nutritions"] = selector.xpath('//div[contains(text(), "Nutritional")]/following-sibling::div//p/text()').get()
            if not data["nutritions"]:
                nut_match = re.search(r'(?:Nutritional Information|Nutrition Facts)\s*:?\s*(.*?)(?:\s*(?:Ingredients|Manufacturer|Country|Seller)|$)', all_text, re.IGNORECASE | re.DOTALL)
                if nut_match:
                    data["nutritions"] = nut_match.group(1).strip(": ")
            
            data["nutritional_information"] = data["nutritions"]

        # Instructions / Care
        if not data["instructions"]:
            data["instructions"] = selector.xpath('//div[contains(text(), "Instructions")]/following-sibling::div//p/text()').get()
            if not data["instructions"]:
                inst_match = re.search(r'(?:Instructions|Usage|Direction)\s*:?\s*(.*?)(?:\s*(?:Ingredients|Manufacturer|Country|Seller)|$)', all_text, re.IGNORECASE | re.DOTALL)
                if inst_match:
                    data["instructions"] = inst_match.group(1).strip(": ")
            
            data["instructionforuse"] = data["instructions"]

        # Breadcrumb fallback from URL or common patterns
        if not data["breadcrumb"]:
            # Often Swiggy uses a header or specific class for breadcrumbs
            bc_items = selector.css('div[class*="Breadcrumb"] a::text').getall() or \
                       selector.css('ol[class*="breadcrumb"] li a::text').getall()
            
            if bc_items:
                data["breadcrumb"] = " > ".join(bc_items)
                data["producthierarchy_level1"] = bc_items[0] if len(bc_items) > 0 else None
                data["producthierarchy_level2"] = bc_items[1] if len(bc_items) > 1 else None
                data["producthierarchy_level3"] = bc_items[2] if len(bc_items) > 2 else None
            else:
                # Try to infer from URL parts
                url_parts = data["url"].replace('https://www.swiggy.com/instamart/p/', '').split('/')
                if len(url_parts) > 1:
                    data["breadcrumb"] = " > ".join([p.replace('-', ' ').title() for p in url_parts[:-1]])

    @staticmethod
    def _calculate_discount(data):
        """Calculate percentage discount if prices are available."""
        try:
            mrp = float(data["regular_price"])
            price = float(data["selling_price"])
            if mrp > 0 and price < mrp:
                data["percentage_discount"] = round(((mrp - price) / mrp) * 100, 2)
        except:
            pass

    @staticmethod
    def _clean_data(data):
        """Clean up strings and ensure consistency. Use empty strings for missing values."""
        for k, v in data.items():
            if v is None:
                data[k] = ""
            elif isinstance(v, str):
                data[k] = v.strip()
            
            # If after stripping it's empty, or still None, make sure it's ""
            if data[k] is None or data[k] == "":
                data[k] = ""

if __name__ == "__main__":
    import json
    import time
    import random
    from curl_cffi import requests as curl_requests
    from pymongo import MongoClient
    
    # --- CONFIGURATION ---
    # This block allows you to run the parser standalone to backfill your database.
    print("--- Swiggy Parser Standalone Utility ---")
    
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    url_collection = db[settings.MONGO_COLLECTION_PRODUCT]
    details_collection = db[settings.MONGO_COLLECTION_PRODUCT_DETAILS]
    
    # 1. Fetch all product URLs from the basic collection
    products = list(url_collection.find({}, {"url": 1, "product_name": 1}))
    total = len(products)
    print(f"Found {total} products in '{settings.MONGO_COLLECTION_PRODUCT}' to process.")
    
    session = curl_requests.Session()
    success_count = 0
    
    for i, prod in enumerate(products, 1):
        url = prod.get("url")
        if not url: continue
        
        # Check if we already have this in details
        if details_collection.find_one({"url": url}):
            print(f"[{i}/{total}] Skipping already processed: {url}")
            success_count += 1
            continue
            
        print(f"[{i}/{total}] Parsing: {url}")
        
        try:
            impersonate, headers, cookies = settings.get_manual_config()
            response = session.get(
                url, 
                headers=headers, 
                cookies=cookies,
                impersonate=impersonate,
                timeout=settings.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = SwiggyParser.extract_data(response.text, url)
                data["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
                
                # Save to details collection
                details_collection.update_one(
                    {"url": url},
                    {"$set": data},
                    upsert=True
                )
                success_count += 1
                print(f"    -> Saved details for: {data.get('product_name')}")
            else:
                print(f"    -> Failed! HTTP {response.status_code}")
                
            # Random sleep to be safe
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"    -> Error: {e}")
            time.sleep(5)
            
    print(f"\n--- Process Finished! ---")
    print(f"Total Products: {total}")
    print(f"Processed/Details in DB: {success_count}")
    client.close()
