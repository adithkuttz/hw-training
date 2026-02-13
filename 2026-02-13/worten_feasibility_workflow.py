import requests
from scrapy import Selector
import json
import pandas as pd
import time

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.worten.pt/informatica-e-acessorios?__cf_chl_tk=1_4wDtuLa.E2ngnrQFuAXyhCXvnsC8gl3pbvn1u26Tw-1770960286-1.0.1.1-5X5qANx7IfYOY2XSGNZftykLHZhhEJjqWHBt.X5WzHE',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"143.0.7499.192"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="143.0.7499.192", "Chromium";v="143.0.7499.192", "Not A(Brand";v="24.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Linux"',
    'sec-ch-ua-platform-version': '""',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    # 'cookie': 'feature-hestia-session-no-graphql=true; feature-incubeta-view-events=true; wrand=1; sts=763a91b6d6c4c87a8e87ea7e7c2430f98a3f5a96c1e73c33ab643d0958444992; feature_client_area_resolve_repair_form=true; sales_features=air_conditioning; is_sced_feature_active=true; is_long_tail_items_active=true; suggestions_behavior=with_categories,ignore_analytics,cms_categories; feature-search-default-category-breadcrumbs=true; feature_use_mandrake_fetch_resolve=true; feature_allow_services_for_marketplace=true; feature-pickup-details-enabled=true; with_categories=true; feature_new_sced_on=true; feature_use_atena_services=true; feature-enable-mirakl-ads=true; feature-add-request-count-logs=true; feature_mfa=true; feature_applepay_provider=true; feature_incubeta=true; feature-observe-cross-sell-services-badges-headers-error=true; feature_client_area_resolve_services=true; rr_rcs=eF5jYSlN9jA0TbQwNDM21jVLNjHXNUlMS9M1MTA01zW3MDM3NDFOMk8xSOXKLSvJTBEwNDSy0DXUNQQAf7ENpg; CookieConsent={stamp:%27gUU0QjzzCHpp6CEwQ5Rh/o1Rfj6MmcZEhm2+c6jprj7PfVLL3CErXw==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1770884761624%2Cregion:%27in%27}; _gcl_au=1.1.1433887860.1770884762; _hjSessionUser_1680786=eyJpZCI6IjIxZmI4N2IzLTU1NWUtNTAxNS05YWZkLTcwMjg2YzBkYWJiYyIsImNyZWF0ZWQiOjE3NzA4ODQ3NjIzODQsImV4aXN0aW5nIjp0cnVlfQ==; _ga=GA1.1.1539621866.1770884760; feature_worten_life=true; feature-loyalty-membership-v2=true; feature_continente_consents=false; feature_googlepay_provider=true; feature-home-plan=true; feature_applepay_provider_v2=true; feature-pub-store-electronic-invoice-hestia=true; FPID=FPID2.2.8xDh2MnHu%2BTn0%2Fi2ecjqFdds2L3e%2BbWvpLeCnLlBky8%3D.1770884760; h2h-cookie=A; kk_leadtag=true; _pin_unauth=dWlkPU1HVXdPREkzTVRNdE1qQTVNQzAwWXpObUxXSXdaVEV0Wm1Oa01qRTNaR1k0TjJJeA; mirakl-ads-uuid=8a98a5b0-e26f-43c6-8d40-8c703559e478; _fbp=fb.1.1770897863602.277121509794651427; _tt_enable_cookie=1; _ttp=01KH8VSX55ZP27VC8MG7JVXSMT_.tt.1; _rdt_uuid=1770897863216.f13b3535-eed0-41ca-9bc4-c0d8c822a6c4; _rdt_em=:21348728070e9d603508aac52c1e54ecc92283c29ab251078d618c3914e3ac7d,d08fdd1612736e5fb2561a7fa651e5003b3ae4034e0cf7bf039f16648ba914d5,a3f78f09875516d343e35d8174b099897f8aa0aaeda06885f883a40b2d58977f; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22%22%2C%22expiryDate%22%3A%222027-02-12T12%3A43%3A49.824Z%22%7D; ttcsid=1770897863850::DHorP5Qhe4qz70dVhYRM.1.1770900230976.0; ttcsid_C5JHC7VGE0M3SF4JSP00=1770897863849::ujM9Zxb0u71Pf7rGFEiZ.1.1770900230976.1; cto_bundle=iUEUOl9uSTNtRWpkaFVqejN1OVFvZ1Z3UTAxeVJuSFNuQUlHcFhGZXhVaUhBa2JDR3JGeCUyQnZDUG50UmoxQ2t5TG56QXJkS3FYNTEzc2lTaUxxQnl1RzZiQ0dhUSUyQkRBTWpydnl6WVdhNm52MHYwbnNBQURqVjNkSUtNV1JyeiUyQk5FUkc2S2ZPQnpOZXBhTVdaUlhCMmY5MjFETHclM0QlM0Q; tfpsi=3044bd28-da7e-42c8-87aa-c74b4ebcecb8; FPLC=70BXGnBM0P2dIdVXwtd3kwAjhqaUoKf1PeFV6GZ1kyrUR0losGwmU0oV3VeMq9okmliuR40nTHbIpbG19%2BhNtNQYIWAWxih9CBx%2Fx%2Bb1zXYm0EyNlCMi6ugAN18nHw%3D%3D; cf_clearance=coH5kyRPfG4mlsxhE6CA3.1T_tdGXPQPb830WDT3dMM-1770960290-1.2.1.1-dyQxKYBXAjd7c5wMr8JIlCTTvXepUqK3YhxS2itHamGxdU1hBHJJFdHxVlZArZ4d8CAXsMT3SXRT.e5WVgODHuI1xKf.XKfmlan.hqdtRReg6EFg4KXqDm1fk5xEs8gdxcbmwQTzpNmMVs1P4avBe4uqkP6WmaomKnqH3Z7zocLw4VqOoPN0E6nPN6UxYs8JjLzviBqJTl4T6coCmUiY8YOKHU0iJUm1.5ewexB5aG4; _ga_WM5ETPQSYP=GS2.1.s1770958027$o5$g1$t1770960373$j58$l0$h0; _ga_780GS19BPN=GS2.1.s1770958027$o5$g1$t1770960373$j58$l0$h1564883842; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22aW2bxITm1almMF5jpGfa%22%2C%22expiryDate%22%3A%222027-02-13T05%3A26%3A13.321Z%22%7D; rr_rcs=eF5jYSlN9jA0TbQwNDM21jVLNjHXNUlMS9M1MTA01zW3MDM3NDFOMk8xSOXKLSvJTBEwNDSy0DXUNQQAf7ENpg; g_state={"i_l":0,"i_ll":1770960375744,"i_b":"CZKbg+BaNcFIQonedzRyl+UeEjFillwA/uYOIinRSjU","i_e":{"enable_itp_optimization":0}}',
}


all_data = []

                                                  #CRAWLER 

sitemap_url = "https://www.worten.pt/productssitemap.xml"
response = requests.get(sitemap_url, headers=headers)
selector = Selector(text=response.text)

product_urls = selector.xpath("//loc/text()").getall()

                                             #PARSER 

for pdp_url in product_urls:

    if "/produtos/" not in pdp_url:
        continue

    print("Scraping:", pdp_url)

    try:
        response = requests.get(pdp_url, headers=headers)
        selector = Selector(text=response.text)

        data = {}

      
        data["url"] = pdp_url
        data["unique_id"] = pdp_url.split("-")[-1]
        data["productname"] = selector.xpath("//h1/text()").get()
        data["selling_price"] = selector.xpath(
            "//span[contains(@class,'price')]/text()"
        ).get()
        data["regular_price"] = selector.xpath(
            "//span[contains(@class,'old')]/text()"
        ).get()
        data["brand"] = selector.xpath(
            "//a[contains(@href,'marca')]/text()"
        ).get()
        data["rating"] = selector.xpath(
            "//span[contains(@class,'rating')]/text()"
        ).get()
        data["review"] = selector.xpath(
            "//span[contains(text(),'avalia')]/text()"
        ).get()
        desc = selector.xpath(
            "//div[contains(@class,'about')]//text()"
        ).getall()
        data["description"] = " ".join(desc).strip()
        specs = selector.xpath("//table//text()").getall()
        data["specification"] = " ".join(specs).strip()
        data["image"] = selector.xpath("//img/@src").get()
        data["colour"] = selector.xpath(
            "//*[contains(text(),'Cor')]/following::span[1]/text()"
        ).get()


        all_data.append(data)

        time.sleep(1)   

    except Exception as e:
        print("Error:", e)


df = pd.DataFrame(all_data)
df.to_csv("worten_products.csv", index=False)

print("DONE")
