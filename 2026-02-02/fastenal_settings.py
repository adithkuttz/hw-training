
BASE_URL = "https://www.fastenal.com/catalog/api/product-search"

ENDPOINT_URL = "https://www.fastenal.com/catalog/api/product-search"


COOKIES = {
    'XSRF-TOKEN': 'e57685b2-8887-44f5-ab2b-bcced7f07095',
    'mt.v': '2.130758829.1769581731104',
    '_fbp': 'fb.1.1769581731607.944767968122550614',
    '_ga': 'GA1.1.1943698903.1769581732',
    'sa-r-source': 'chatgpt.com',
    'sa-user-id': 's%253A0-19cbb878-bc57-543e-5a83-60684500bd64.rVJwsCFx93C19rWS5fyqsVFevSCfKwLA0dznO0JuFr0',
    'sa-user-id-v2': 's%253AGcu4eLxXVD5ag2BoRQC9ZGexG3k.RJBpFwGVRpISyZaG1DV13ko2%252BW4051UJuKj0vxDj0pc',
    'sa-user-id-v3': 's%253AAQAKIEH5-rwebMOcjgwMddaWNGF-aumKBMRbd8_p20bKxKRbEAEYAyC5vo_LBjABOgSq5aCgQgQw8GXC.Smy37iZSZ19dLF6lV%252F6cd2lcSHOlKjzmZL5SDeJdgEk',
    'srch_ver': 'v5',
    'COOKIE_AGREEMENT': '"1"',
    'usr_typ': 'external',
    'sa-r-date': '2026-01-29T07:38:29.999Z',
    'CJSESSIONID': 'ZmVkYWI0MDAtMzZkNS00OWE4LWJjYzktZjk5NjIwZGFjZWVk',
    '_clck': 'oljki8%5E2%5Eg35%5E0%5E2219',
    '_clsk': '7wicov%5E1769749114603%5E21%5E1%5Ewww.clarity.ms%2Feus2-e%2Fcollect',
    '_ga_X40YWNGS17': 'GS2.1.s1769748460$o8$g1$t1769749118$j35$l0$h0',
    '_uetsid': '9d58db40fc1211f0bb3139cfa0a7ba15',
    '_uetvid': '9d591c50fc1211f087c945652bd264a1',
}

HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.fastenal.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.fastenal.com/product/Abrasives/Sanding%20Abrasives%20Products?categoryId=600955',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'x-xsrf-token': 'e57685b2-8887-44f5-ab2b-bcced7f07095',
    # 'cookie': 'XSRF-TOKEN=e57685b2-8887-44f5-ab2b-bcced7f07095; mt.v=2.130758829.1769581731104; _fbp=fb.1.1769581731607.944767968122550614; _ga=GA1.1.1943698903.1769581732; sa-r-source=chatgpt.com; sa-user-id=s%253A0-19cbb878-bc57-543e-5a83-60684500bd64.rVJwsCFx93C19rWS5fyqsVFevSCfKwLA0dznO0JuFr0; sa-user-id-v2=s%253AGcu4eLxXVD5ag2BoRQC9ZGexG3k.RJBpFwGVRpISyZaG1DV13ko2%252BW4051UJuKj0vxDj0pc; sa-user-id-v3=s%253AAQAKIEH5-rwebMOcjgwMddaWNGF-aumKBMRbd8_p20bKxKRbEAEYAyC5vo_LBjABOgSq5aCgQgQw8GXC.Smy37iZSZ19dLF6lV%252F6cd2lcSHOlKjzmZL5SDeJdgEk; srch_ver=v5; COOKIE_AGREEMENT="1"; usr_typ=external; sa-r-date=2026-01-29T07:38:29.999Z; CJSESSIONID=ZmVkYWI0MDAtMzZkNS00OWE4LWJjYzktZjk5NjIwZGFjZWVk; _clck=oljki8%5E2%5Eg35%5E0%5E2219; _clsk=7wicov%5E1769749114603%5E21%5E1%5Ewww.clarity.ms%2Feus2-e%2Fcollect; _ga_X40YWNGS17=GS2.1.s1769748460$o8$g1$t1769749118$j35$l0$h0; _uetsid=9d58db40fc1211f0bb3139cfa0a7ba15; _uetvid=9d591c50fc1211f087c945652bd264a1',
}


#mongodb configuration

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "fastenal"
COLLECTION_NAME = "fastenal_category"

ROOT_CATEGORY_ID = "600948"
ROOT_CATEGORY_NAME = "Abrasives"
