import requests
import pandas as pd
import time

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'matcher': 'gbada8ee977ae8dadefcfad',
    'origin': 'https://www.swiggy.com',
    'priority': 'u=1, i',
    'referer': 'https://www.swiggy.com/instamart/city/bangalore/c/tea-coffee-and-more',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'x-build-version': '2.324.0',
    'x-request-source': 'SEO',
    # 'cookie': 'deviceId=s%3Ad691cd5b-0e60-4f0d-b0a3-83a8487704ae.SEsTLYRbQH9%2FFRtyAtm1w7E0FbILcC4bOduqqEhSxeA; tid=s%3Ad357a202-c948-44e6-bc77-af115186db87.jyINDEp5HpOzR%2FLTI%2FrtkWK1GP6kodR7of49Z4eOmGE; sid=s%3Apwb27882381-1fae-4eee-a398-b452cc778.l%2FKPV3nvMbhy9skSPA6%2BMwZT7TyTIq6L2avgC0q9wNk; versionCode=1200; platform=web; subplatform=dweb; statusBarHeight=0; bottomOffset=0; genieTrackOn=false; ally-on=false; isNative=false; strId=; openIMHP=false; webBottomBarHeight=0; _gcl_au=1.1.1737435483.1771999075; _ga=GA1.1.261626594.1771999075; _fbp=fb.1.1771999075000.432118399609086224; moe_uuid=b1480884-eb20-40b9-925b-06743c47049a; imOrderAttribution={%22entryId%22:%22tea%20and%20coffee%22%2C%22entryName%22:%22instamartOpenSearch%22}; lat=s%3A12.960059122809971.h096G6jFEvdKvA%2FcX99%2BU8AUppIjzSJe1T91Va8STTA; lng=s%3A77.57337538383284.wugDnemZ%2FtGrNMd6ngGjUURS0PQobZYKKuJR5ywS5qU; address=s%3Aundefined.H4tl815DCZ6%2Fo5v13eAn2NGFexz2evmgMlUcBAJMXS8; addressId=s%3Aundefined.H4tl815DCZ6%2Fo5v13eAn2NGFexz2evmgMlUcBAJMXS8; LocSrc=s%3AseoCty.Ln0AZvvgsCPuKj5IAqQw2NnSsBG0BSCZyoU1v9a5kXs; userLocation=%7B%22lat%22%3A%2212.960059122809971%22%2C%22lng%22%3A%2277.57337538383284%22%7D; aws-waf-token=aafb3b7b-bfa3-472a-92de-3b982203dbf0:HgoAjlcxkIblAAAA:+a6i7xeC9LOw+Ed0JrBOKbnKkc4HgnTeIPFmThXw/4eL3/dSEmDpatutwWhAFYuGA8UR/s+e2erCALqmjkaUxr/FWNBleIzE43KrfjCk74cgHO5OpQ8JC6OHax6nRyGExu4shiVozh0Q4Zh40GlTdi3LxARJzVqVfMlixkeMcChUjrLeBxxTeEUm5FLuJyqLWoc+9h4NgKhi4f9Tjyi0/tSB+bhSuFhEyBt6mXPig6AhA9A2wmEAVlRvlSUpr5cuaZB8yhA=; _ga_0XZC5MS97H=GS2.1.s1772001875$o2$g1$t1772003715$j60$l0$h0; _ga_VEG1HFE5VZ=GS2.1.s1772001875$o2$g1$t1772003715$j60$l0$h0; _ga_8N8XRG907L=GS2.1.s1772001875$o2$g1$t1772003715$j60$l0$h0',
}

all_data = []

# -------- PDP URL LIST --------

pdp_urls = [
    "https://www.swiggy.com/instamart/p/bru-instant-coffee-pouch-LLJK7X0ROV",
    "https://www.swiggy.com/instamart/p/taj-mahal-rich-and-flavourful-tea-6HV1APWYR9",
    "https://www.swiggy.com/instamart/p/nescafe-classic-instant-coffee-G71JM2XSG3",
]

# -------- PARSER --------

for pdp_url in pdp_urls:

    print("Scraping:", pdp_url)

    try:
        product_id = pdp_url.split("-")[-1]

        
        api_url = f"https://www.swiggy.com/api/instamart/category-listing/filter/v2?storeId=1181690&primaryStoreId=1181690&secondaryStoreId=1402948&pageNo=1&offset=1&page_name=category_listing_filter"

        response = requests.get(api_url, headers=headers)
        json_data = response.json()
        product = json_data.get("data", {})

        data = {}

        # -------- REQUIRED FIELDS --------

        data["unique_id"] = product_id
        data["competitor_product_key"] = product_id
        data["product_unique_key"] = product_id
        data["pdp_url"] = pdp_url

        breadcrumb = product.get("breadcrumb", [])
        data["breadcrumb"] = " > ".join(breadcrumb) if breadcrumb else None
        data["producthierarchy_level1"] = breadcrumb[0] if len(breadcrumb) > 0 else None
        data["producthierarchy_level2"] = breadcrumb[1] if len(breadcrumb) > 1 else None
        data["producthierarchy_level3"] = breadcrumb[2] if len(breadcrumb) > 2 else None

        data["product_name"] = product.get("name")
        data["brand"] = product.get("brand")

        weight = product.get("weight")
        if weight:
            parts = weight.split()
            data["grammage_quantity"] = parts[0]
            data["grammage_unit"] = parts[1] if len(parts) > 1 else None
        else:
            data["grammage_quantity"] = None
            data["grammage_unit"] = None

        data["regular_price"] = product.get("mrp")
        data["selling_price"] = product.get("price")
        data["percentage_discount"] = product.get("discountPercentage")
        data["currency"] = "INR"

        data["product_description"] = product.get("description")
        data["ingredients"] = product.get("ingredients")
        data["nutritions"] = product.get("nutritionInfo")
        data["nutritional_information"] = product.get("nutritionInfo")
        data["instructions"] = product.get("usageInfo")
        data["instructionforuse"] = product.get("usageInfo")
        data["country_of_origin"] = product.get("countryOfOrigin")

        images = product.get("images", [])
        data["image_url_1"] = images[0] if images else None

        data["instock"] = product.get("inStock")

        all_data.append(data)

        time.sleep(1)

    except Exception as e:
        print("Error:", e)

df = pd.DataFrame(all_data)
df.to_csv("swiggy_products.csv", index=False)

print("DONE")
