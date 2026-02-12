PROJECT_NAME = "lidl"

BASE_URL = "https://www.lidl.co.uk/"
SITEMAP_URL = "https://www.lidl.co.uk/static/sitemap.xml"

MONGO_DB = PROJECT_NAME

MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category_url"
MONGO_COLLECTION_CATEGORY_PLAYWRIGHT = f"{PROJECT_NAME}_category_url_playwright"
MONGO_COLLECTION_CATEGORY_CLOUDSCRAPER = f"{PROJECT_NAME}_category_url_cloudscraper"
MONGO_COLLECTION_CATEGORY_CURL = f"{PROJECT_NAME}_category_url_curl"
MONGO_COLLECTION_CATEGORY_SELENIUM = f"{PROJECT_NAME}_category_url_selenium"   
MONGO_COLLECTION_SUBCATEGORY_PLAYWRIGHT = f"{PROJECT_NAME}_subcategory_url_playwright"


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
