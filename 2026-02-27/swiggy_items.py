from mongoengine import connect, Document, DynamicDocument, StringField, ListField, DateTimeField, FloatField, BooleanField
import swiggy_settings as settings
from datetime import datetime

# Initialize MongoEngine Connection
connect(
    db=settings.MONGO_DB, 
    host=settings.MONGO_URI,
    alias="default"
)

class SwiggyProductDetail(Document):
    """
    Swiggy Instamart Detailed Product Item using MongoEngine
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_PRODUCT_DETAILS
    }

    # Identification Fields
    unique_id = StringField(default="")
    url = StringField(unique=True, required=True)
    competitor_product_key = StringField(default="")
    product_unique_key = StringField(default="")

    # Product Info
    product_name = StringField(default="")
    brand = StringField(default="")
    product_description = StringField(default="")
    
    # Hierarchy
    breadcrumb = StringField(default="")
    producthierarchy_level1 = StringField(default="")
    producthierarchy_level2 = StringField(default="")
    producthierarchy_level3 = StringField(default="")

    # Pricing & Quantity
    regular_price = StringField(default="")
    selling_price = StringField(default="")
    percentage_discount = StringField(default="") # String to match user's parser output ("")
    currency = StringField(default="INR")
    grammage_quantity = StringField(default="")
    grammage_unit = StringField(default="")

    # Additional Details
    ingredients = StringField(default="")
    nutritions = StringField(default="")
    nutritional_information = StringField(default="")
    instructions = StringField(default="")
    instructionforuse = StringField(default="")
    country_of_origin = StringField(default="")
    
    # Media & Status
    image_url_1 = StringField(default="")
    instock = StringField(default="") # String to handle "" instead of Boolean
    
    # Metadata
    last_updated = StringField(default="")
    date_added = DateTimeField(default=datetime.utcnow)

class SwiggyProduct(Document):
    """
    Basic Product Information (Original Collection)
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_PRODUCT
    }
    
    url = StringField(unique=True, required=True)
    product_name = StringField(default="")
    source_url = StringField(default="")
    last_updated = StringField(default="")

class SwiggySubcategoryUrl(DynamicDocument):
    """
    Collection for discovered subcategory URLs
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_SUBCATEGORY
    }
    
    url = StringField(unique=True, required=True)
    category_name = StringField(default="")
    processed = StringField(default="false")
