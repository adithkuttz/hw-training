import requests
from parsel import Selector
from datetime import datetime
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.lidl.co.uk/',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}


#category_url extraction
url = "https://www.lidl.co.uk/static/sitemap.xml"
response = requests.get(url, headers=headers)

selector = Selector(text=response.text)

product_links = selector.xpath('//a[contains(@class, "base-navigation-tree__link") and starts-with(@href, "/products/")]/@href').getall()


######################crawler######################

url = https://www.lidl.co.uk/c/food-drink/s10068374
response = requests.get(url, headers=headers)
selector = Selector(text=response.text)

#extract product urls
product_urls = selector.xpath("//div[contains(@class, 'product-tile')]//a[contains(@class, 'product-tile__link')]/@href").getall()
for product in product_urls:
    full_product_url = f"https://www.aldi.us{product}"  
#pagination
next_page = selector.xpath('//a[@aria-label="Next"]/@href').get()

######################Parser######################

url = https://www.lidl.co.uk/p/deluxe-australia-viognier-riverina/p10028190
response = requests.get(url, headers=headers)
selector = Selector(text=response.text)
competitor_name = "lidl"   # change per site
pdp_url = url
extraction_date = datetime.now().strftime("%Y-%m-%d")

product_name = get_text(selector, "//h1/text()")
brand = get_text(selector, '//a[contains(@class,"brand")]//text()')

description = get_all_text(selector,
    '//div[contains(@class,"description")]//text()'
)
unique_id = url.split("-")[-1] if "-" in url else ""
competitor_product_key = unique_id
product_unique_key = f"{unique_id}P"
breadcrumbs = selector.xpath("//nav//a/text()").getall()
breadcrumb = " > ".join(breadcrumbs) if breadcrumbs else ""
producthierarchy_level1 = breadcrumbs[0] if len(breadcrumbs) > 0 else ""
producthierarchy_level2 = breadcrumbs[1] if len(breadcrumbs) > 1 else ""
instock = "TRUE" if selector.xpath('//button[contains(.,"Add")]') else "FALSE"
uom_text = get_text(selector,
    '//span[contains(@class,"unit")]//text()'
)
grammage_quantity = ""
grammage_unit = ""
netcontent = uom_text
netweight = uom_text
if uom_text:
    parts = uom_text.split()
    if len(parts) == 2:
        grammage_quantity = parts[0]
        grammage_unit = parts[1]
image_url_1 = get_text(selector,
    '//img[contains(@class,"product-image")]/@src'
)
file_name_1 = image_url_1.split("/")[-1] if image_url_1 else ""
selling_price = get_text(selector,
    '//span[contains(@class,"base-price")]//text()'
)
regular_price = get_text(selector,
    '//span[contains(@class,"wasPrice")]//text()'
)
promotion_price = selling_price   # usually same
percentage_discount = get_text(selector,
    '//div[contains(@class,"discount")]//text()'
)

#############################Findings############################

#126 fields where given but all fields are not available in the website
