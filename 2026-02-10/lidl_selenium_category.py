
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymongo
from lidl_settings import (
    BASE_URL,
    MONGO_DB,
    MONGO_COLLECTION_CATEGORY_SELENIUM,
    HEADERS
)

def scrape():
    print("Starting Selenium Scraper...")
    
    # 1. Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION_CATEGORY_SELENIUM]

    # 2. Setup Selenium
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Comment out to see the browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Add headers as argument if possible, or just rely on default
    chrome_options.add_argument(f"user-agent={HEADERS['User-Agent']}")

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 3. Fetch Base URL
        driver.get(BASE_URL)
        time.sleep(3) # Wait for page load

        # Handle cookies if present (simple check)
        try:
            # Example cookie button - replace with actual if found, but exploration didn't show one
            cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
            cookie_btn.click()
            time.sleep(1)
        except:
            pass

        # 4. Extract Main Categories
        # Using the same XPath strategy
        main_categories_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'n-header__main-navigation-link')]")
        
        main_categories = []
        for cat in main_categories_elements:
            url = cat.get_attribute("href")
            name = cat.text.strip()
            if url:
                main_categories.append({"name": name, "url": url})
        
        print(f"Found {len(main_categories)} main categories.")

        # 5. Iterate Categories
        for cat_data in main_categories:
            print(f"Processing Category: {cat_data['name']} - {cat_data['url']}")
            
            # Save Category
            cat_doc = {
                "name": cat_data['name'],
                "url": cat_data['url'],
                "type": "category"
            }
            collection.update_one({"url": cat_data['url']}, {"$set": cat_doc}, upsert=True)

            try:
                driver.get(cat_data['url'])
                time.sleep(3)
                
                # Extract Subcategories
                # Strategy: Look for the card items again
                sub_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'ATheContentPageCardList__Item')]")
                
                print(f"  Found {len(sub_elements)} subcategories.")
                
                for sub in sub_elements:
                    sub_url = sub.get_attribute("href")
                    sub_name = sub.text.strip()
                    
                    if sub_url:
                        sub_doc = {
                            "name": sub_name,
                            "url": sub_url,
                            "parent_category": cat_data['name'],
                            "type": "subcategory"
                        }
                        collection.update_one({"url": sub_url}, {"$set": sub_doc}, upsert=True)
                        print(f"    Saved Subcategory: {sub_name}")
                        
            except Exception as e:
                print(f"  Error processing category {cat_data['name']}: {e}")

    finally:
        driver.quit()
        print("Selenium Scraper Finished.")

if __name__ == "__main__":
    scrape()
