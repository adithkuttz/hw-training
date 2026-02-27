import random

# ---------- PROJECT CONFIG ----------
PROJECT_NAME = "swiggy_instamart"
BASE_URL = "https://www.swiggy.com/instamart"
FILE_NAME_FULLDUMP = f"{PROJECT_NAME}_products_dump.csv"


# ---------- MONGO CONFIG ----------
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = PROJECT_NAME
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_categories"
MONGO_COLLECTION_SUBCATEGORY = f"{PROJECT_NAME}_subcategory_urls"
MONGO_COLLECTION_PRODUCT = f"{PROJECT_NAME}_products"
MONGO_COLLECTION_PRODUCT_DETAILS = f"{PROJECT_NAME}_product_details"


# ---------- MANUAL BYPASS CONFIG ----------
# FRESH COOKIES UPDATED 2026-02-17
# Note: User-Agent synchronized with chrome120 impersonation to avoid Cloudflare detection
MANUAL_HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'matcher': 'ff9fc8ee97fegfcb9dfb79b',
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
    'x-build-version': '2.325.0',
    'x-request-source': 'SEO',
    # 'cookie': 'deviceId=s%3Ad691cd5b-0e60-4f0d-b0a3-83a8487704ae.SEsTLYRbQH9%2FFRtyAtm1w7E0FbILcC4bOduqqEhSxeA; versionCode=1200; platform=web; subplatform=dweb; statusBarHeight=0; bottomOffset=0; genieTrackOn=false; ally-on=false; isNative=false; strId=; openIMHP=false; webBottomBarHeight=0; _gcl_au=1.1.1737435483.1771999075; _ga=GA1.1.261626594.1771999075; _fbp=fb.1.1771999075000.432118399609086224; moe_uuid=b1480884-eb20-40b9-925b-06743c47049a; address=s%3Aundefined.H4tl815DCZ6%2Fo5v13eAn2NGFexz2evmgMlUcBAJMXS8; addressId=s%3Aundefined.H4tl815DCZ6%2Fo5v13eAn2NGFexz2evmgMlUcBAJMXS8; LocSrc=s%3AseoCty.Ln0AZvvgsCPuKj5IAqQw2NnSsBG0BSCZyoU1v9a5kXs; lat=s%3A12.960059122809971.h096G6jFEvdKvA%2FcX99%2BU8AUppIjzSJe1T91Va8STTA; lng=s%3A77.57337538383284.wugDnemZ%2FtGrNMd6ngGjUURS0PQobZYKKuJR5ywS5qU; userLocation=%7B%22lat%22%3A%2212.960059122809971%22%2C%22lng%22%3A%2277.57337538383284%22%7D; tid=s%3Aca94ce0f-294b-4361-bf02-b1ce1c6ee77d.75fWxbNkLWX1edgKsAEMzGc7YwCHefZA6Io9XwiwLNg; sid=s%3Apwz183cd384-bdf8-437f-8126-d73ed966f.OIqHnCBmyKfx3hoohPflWU6WuTDlC3SBTT5R7hyacEM; _ga_0XZC5MS97H=GS2.1.s1772087165$o5$g1$t1772087985$j59$l0$h0; _ga_VEG1HFE5VZ=GS2.1.s1772087166$o5$g1$t1772087985$j59$l0$h0; _ga_8N8XRG907L=GS2.1.s1772087166$o5$g1$t1772087985$j59$l0$h0; aws-waf-token=4ebb3b45-b4c1-49a2-a48d-c19788eb7a5c:HgoAqtMtz1PCAAAA:0Pa+MirvcQLKqyzUrlpac/ZfH0EfqIPRi4HE0ozlUvqHAXtTIb/jL+xUswiUK6+Td4S/ZHX1aoT0Q6Mrvzk+hkPv1i8A0hC6IucupvXIgnTMtTtTC+UtkZHm9VBcWByVP49sLFcvLa8KJeUMli3H7uQvsXQfVrP8tQKH0oeoufnLKsbfiUQfmZXLLMm5HRezwZHzHFB9hN4QU80KfYM6jXtgz+ijJK4GxOf60pXr+kUuS8SJyzd9xTC23LgXLJl4dB77bfc=',
}
MANUAL_COOKIES = {
    'deviceId': 's%3Ad691cd5b-0e60-4f0d-b0a3-83a8487704ae.SEsTLYRbQH9%2FFRtyAtm1w7E0FbILcC4bOduqqEhSxeA',
    'versionCode': '1200',
    'platform': 'web',
    'subplatform': 'dweb',
    'statusBarHeight': '0',
    'bottomOffset': '0',
    'genieTrackOn': 'false',
    'ally-on': 'false',
    'isNative': 'false',
    'strId': '',
    'openIMHP': 'false',
    'webBottomBarHeight': '0',
    '_gcl_au': '1.1.1737435483.1771999075',
    '_ga': 'GA1.1.261626594.1771999075',
    '_fbp': 'fb.1.1771999075000.432118399609086224',
    'moe_uuid': 'b1480884-eb20-40b9-925b-06743c47049a',
    'address': 's%3Aundefined.H4tl815DCZ6%2Fo5v13eAn2NGFexz2evmgMlUcBAJMXS8',
    'addressId': 's%3Aundefined.H4tl815DCZ6%2Fo5v13eAn2NGFexz2evmgMlUcBAJMXS8',
    'LocSrc': 's%3AseoCty.Ln0AZvvgsCPuKj5IAqQw2NnSsBG0BSCZyoU1v9a5kXs',
    'lat': 's%3A12.960059122809971.h096G6jFEvdKvA%2FcX99%2BU8AUppIjzSJe1T91Va8STTA',
    'lng': 's%3A77.57337538383284.wugDnemZ%2FtGrNMd6ngGjUURS0PQobZYKKuJR5ywS5qU',
    'userLocation': '%7B%22lat%22%3A%2212.960059122809971%22%2C%22lng%22%3A%2277.57337538383284%22%7D',
    'tid': 's%3Aca94ce0f-294b-4361-bf02-b1ce1c6ee77d.75fWxbNkLWX1edgKsAEMzGc7YwCHefZA6Io9XwiwLNg',
    'sid': 's%3Apwz183cd384-bdf8-437f-8126-d73ed966f.OIqHnCBmyKfx3hoohPflWU6WuTDlC3SBTT5R7hyacEM',
    '_ga_0XZC5MS97H': 'GS2.1.s1772087165$o5$g1$t1772087985$j59$l0$h0',
    '_ga_VEG1HFE5VZ': 'GS2.1.s1772087166$o5$g1$t1772087985$j59$l0$h0',
    '_ga_8N8XRG907L': 'GS2.1.s1772087166$o5$g1$t1772087985$j59$l0$h0',
    'aws-waf-token': '4ebb3b45-b4c1-49a2-a48d-c19788eb7a5c:HgoAqtMtz1PCAAAA:0Pa+MirvcQLKqyzUrlpac/ZfH0EfqIPRi4HE0ozlUvqHAXtTIb/jL+xUswiUK6+Td4S/ZHX1aoT0Q6Mrvzk+hkPv1i8A0hC6IucupvXIgnTMtTtTC+UtkZHm9VBcWByVP49sLFcvLa8KJeUMli3H7uQvsXQfVrP8tQKH0oeoufnLKsbfiUQfmZXLLMm5HRezwZHzHFB9hN4QU80KfYM6jXtgz+ijJK4GxOf60pXr+kUuS8SJyzd9xTC23LgXLJl4dB77bfc=',
}

def get_manual_config():
    """Return a COPY of the manual bypass config to prevent accidental side effects."""
    headers = MANUAL_HEADERS.copy()
    cookies = MANUAL_COOKIES.copy()
    return "chrome120", headers, cookies

# ---------- AUTOMATIC ROTATION CONFIG ----------
BROWSER_CONFIGS = [
    {
        "impersonate": "chrome120",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec_ch_ua_platform": '"Windows"'
    },
    {
        "impersonate": "chrome119",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Not_A Brand";v="8", "Chromium";v="119", "Google Chrome";v="119"',
        "sec_ch_ua_platform": '"Windows"'
    }
]

def get_session_config(is_homepage=False):
    """Return a COPY of an automatic rotation config."""
    config = random.choice(BROWSER_CONFIGS)
    headers = {
        "User-Agent": config["user_agent"],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "sec-ch-ua": config["sec_ch_ua"],
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": config["sec_ch_ua_platform"],
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none" if is_homepage else "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }
    return config["impersonate"], headers

# ---------- RETRY CONFIG ----------
RETRY_MAX_ATTEMPTS = 5
RETRY_BACKOFF_FACTOR = 5
REQUEST_TIMEOUT = 30
