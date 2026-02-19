from mongoengine import connect, Document, DynamicDocument, StringField, ListField, DateTimeField
import worten_settings as settings
from datetime import datetime

# Initialize MongoEngine Connection
connect(
    db=settings.MONGO_DB, 
    host=settings.MONGO_URI,
    alias="default"
)

class ProductItem(Document):
    """
    Worten Product Item following MongoEngine Document structure
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_PRODUCT
    }

    # Field definitions based on Worten project - Reordered as per user request
    unique_id = StringField()
    url = StringField(unique=True)
    productname = StringField()
    brand = StringField()
    selling_price = StringField()
    regular_price = StringField()
    discount = StringField()
    description = StringField()
    specification = StringField()
    image = StringField()
    rating = StringField()
    review = StringField()
    size = StringField()
    colour = StringField()
    
    # Category context fields (kept for DB structure)
    main_category = StringField()
    subcategory_name = StringField()
    parent_url = StringField()

    
    # Metadata fields
    timestamp = StringField() # Saved as string in scraper
    date_added = DateTimeField(default=datetime.utcnow)

class ProductUrlItem(DynamicDocument):
    """
    Collection for discovered product URLs (used in listing extraction)
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_SUBCATEGORY
    }
    
    product_url = StringField(unique=True)
    categories = ListField() # For category breadcrumbs or hierarchy if added later
