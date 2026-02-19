import random

# ---------- PROJECT CONFIG ----------
PROJECT_NAME = "worten"
BASE_URL = "https://www.worten.pt"
FILE_NAME_FULLDUMP = f"{PROJECT_NAME}_products_dump.csv"


# ---------- MONGO CONFIG ----------
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = PROJECT_NAME
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_categories"
MONGO_COLLECTION_SUBCATEGORY = f"{PROJECT_NAME}_subcategory_urls"
MONGO_COLLECTION_PRODUCT = f"{PROJECT_NAME}_products"


# ---------- MANUAL BYPASS CONFIG ----------
# FRESH COOKIES UPDATED 2026-02-17
# Note: User-Agent synchronized with chrome120 impersonation to avoid Cloudflare detection
MANUAL_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"120.0.6099.225"',
    'sec-ch-ua-full-version-list': '"Not_A Brand";v="8.0.0.0", "Chromium";v="120.0.6099.225", "Google Chrome";v="120.0.6099.225"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Linux"',
    'sec-ch-ua-platform-version': '"6.17.0"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    # 'cookie': 'feature-hestia-session-no-graphql=true; feature-incubeta-view-events=true; wrand=1; sts=763a91b6d6c4c87a8e87ea7e7c2430f98a3f5a96c1e73c33ab643d0958444992; feature_client_area_resolve_repair_form=true; sales_features=air_conditioning; is_sced_feature_active=true; is_long_tail_items_active=true; suggestions_behavior=with_categories,ignore_analytics,cms_categories; feature-search-default-category-breadcrumbs=true; feature_use_mandrake_fetch_resolve=true; feature_allow_services_for_marketplace=true; feature-pickup-details-enabled=true; with_categories=true; feature_new_sced_on=true; feature_use_atena_services=true; feature-enable-mirakl-ads=true; feature-add-request-count-logs=true; feature_mfa=true; feature_applepay_provider=true; feature_incubeta=true; feature-observe-cross-sell-services-badges-headers-error=true; feature_client_area_resolve_services=true; CookieConsent={stamp:%27gUU0QjzzCHpp6CEwQ5Rh/o1Rfj6MmcZEhm2+c6jprj7PfVLL3CErXw==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1770884761624%2Cregion:%27in%27}; _gcl_au=1.1.1433887860.1770884762; _hjSessionUser_1680786=eyJpZCI6IjIxZmI4N2IzLTU1NWUtNTAxNS05YWZkLTcwMjg2YzBkYWJiYyIsImNyZWF0ZWQiOjE3NzA4ODQ3NjIzODQsImV4aXN0aW5nIjp0cnVlfQ==; _ga=GA1.1.1539621866.1770884760; feature_worten_life=true; feature-loyalty-membership-v2=true; feature_continente_consents=false; feature_googlepay_provider=true; feature-home-plan=true; feature_applepay_provider_v2=true; feature-pub-store-electronic-invoice-hestia=true; FPID=FPID2.2.8xDh2MnHu%2BTn0%2Fi2ecjqFdds2L3e%2BbWvpLeCnLlBky8%3D.1770884760; h2h-cookie=A; kk_leadtag=true; _pin_unauth=dWlkPU1HVXdPREkzTVRNdE1qQTVNQzAwWXpObUxXSXdaVEV0Wm1Oa01qRTNaR1k0TjJJeA; mirakl-ads-uuid=8a98a5b0-e26f-43c6-8d40-8c703559e478; _fbp=fb.1.1770897863602.277121509794651427; _tt_enable_cookie=1; _ttp=01KH8VSX55ZP27VC8MG7JVXSMT_.tt.1; FPLC=C7H8%2FKRU6ajBOLm1hZIAqvPEDMZ28NPHc9mdVRzNopnPyKxuONp56rhr2ciSx6K5gctIb3Vdz4L6O0G50DWVNq2H%2FYcegA5L4Vm3mepe4MnWnxbu5PpA73Nv%2FPcvkw%3D%3D; cf_clearance=4oP2HUw5gDQIgSDJMc.7hkE7c.t_qmYfM9IaPh64nM4-1771318045-1.2.1.1-pe00H_oZBcLvx5BsMjJlS9Bud.W9I0Gfeg0FcQ3k3iITBHBkHEd.cDRjP0ZvumgLLE1Rgop7ar6AKEwVtxgSTpSCH20nLg9YTflvnZWxvnMWAZGslMgMPHB7vZOC6KQAaho3RmBCY3bhjGrBbA9WfXk_f8jijqEvqAhO6HJo0s59fT8nqMa4KUpwHdzi1AyqY3IwCdHvf61yVYkVlcl_1RHMr9KViOn4j5Spw2coMFE; _rdt_uuid=1770897863216.f13b3535-eed0-41ca-9bc4-c0d8c822a6c4; _rdt_em=:21348728070e9d603508aac52c1e54ecc92283c29ab251078d618c3914e3ac7d,d08fdd1612736e5fb2561a7fa651e5003b3ae4034e0cf7bf039f16648ba914d5,a3f78f09875516d343e35d8174b099897f8aa0aaeda06885f883a40b2d58977f; tfpsi=9b9d2bef-07f9-4e2b-a5ec-21f0b5a9de2e; _hjSession_1680786=eyJpZCI6ImUzOWQ1OGRhLTgwYmItNDM0Ny1hYzM4LWI3MzA1YzZkMTRhMyIsImMiOjE3NzEzMTgwNDg4MTIsInMiOjEsInIiOjEsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; rr_rcs=eF5jYSlN9jA0TbQwNDM21jVLNjHXNUlMS9M1MTA01zW3MDM3NDFOMk8xSOXKLSvJTBEwNDSy0DXUNQQAf7ENpg; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22%22%2C%22expiryDate%22%3A%222027-02-17T08%3A47%3A33.465Z%22%7D; ttcsid=1771318048011::QbK-8Qhb_H2YXUjIzYaT.7.1771318058044.0; ttcsid_C5JHC7VGE0M3SF4JSP00=1771318048010::mdrBtUgLnjFRMpWd0dX9.7.1771318058049.1; rr_rcs=eF5jYSlN9jA0TbQwNDM21jVLNjHXNUlMS9M1MTA01zW3MDM3NDFOMk8xSOXKLSvJTBEwNDSy0DXUNQQAf7ENpg; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22aW2bxITm1almMF5jpGfa%22%2C%22expiryDate%22%3A%222027-02-17T08%3A49%3A46.935Z%22%7D; _ga_WM5ETPQSYP=GS2.1.s1771318047$o13$g1$t1771318188$j57$l0$h0; _ga_780GS19BPN=GS2.1.s1771318047$o13$g1$t1771318188$j57$l0$h633469307; g_state={"i_l":0,"i_ll":1771318189587,"i_b":"A9hnmOKaUyl6ZYz8YUtG18H/iEk7y8Eh5fC9S5tCAgM","i_e":{"enable_itp_optimization":0}}; cto_bundle=JXO2AF9uSTNtRWpkaFVqejN1OVFvZ1Z3UTA1eEFvdUxBQ2ZoRWpZY0VvdlVjYXNac09RQjhWSHpRb2l2ekFiNyUyRlh4bjFzbG1lRTRKdXMwUHA0RWdHTWNsenJvWWFMTyUyQmEyY2pVJTJGalRFQ2RGQ283JTJCUEYxVmZVTVliNGhDSHpmZU9OSDhmWTVETGozUHoxWHVFbGFwajl1SGVNZyUzRCUzRA',
}
MANUAL_COOKIES = {
    'feature-hestia-session-no-graphql': 'true',
    'feature-incubeta-view-events': 'true',
    'wrand': '1',
    'sts': '763a91b6d6c4c87a8e87ea7e7c2430f98a3f5a96c1e73c33ab643d0958444992',
    'feature_client_area_resolve_repair_form': 'true',
    'sales_features': 'air_conditioning',
    'is_sced_feature_active': 'true',
    'is_long_tail_items_active': 'true',
    'suggestions_behavior': 'with_categories,ignore_analytics,cms_categories',
    'feature-search-default-category-breadcrumbs': 'true',
    'feature_use_mandrake_fetch_resolve': 'true',
    'feature_allow_services_for_marketplace': 'true',
    'feature-pickup-details-enabled': 'true',
    'with_categories': 'true',
    'feature_new_sced_on': 'true',
    'feature_use_atena_services': 'true',
    'feature-enable-mirakl-ads': 'true',
    'feature-add-request-count-logs': 'true',
    'feature_mfa': 'true',
    'feature_applepay_provider': 'true',
    'feature_incubeta': 'true',
    'feature-observe-cross-sell-services-badges-headers-error': 'true',
    'feature_client_area_resolve_services': 'true',
    'CookieConsent': '{stamp:%27gUU0QjzzCHpp6CEwQ5Rh/o1Rfj6MmcZEhm2+c6jprj7PfVLL3CErXw==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1770884761624%2Cregion:%27in%27}',
    '_gcl_au': '1.1.1433887860.1770884762',
    '_hjSessionUser_1680786': 'eyJpZCI6IjIxZmI4N2IzLTU1NWUtNTAxNS05YWZkLTcwMjg2YzBkYWJiYyIsImNyZWF0ZWQiOjE3NzA4ODQ3NjIzODQsImV4aXN0aW5nIjp0cnVlfQ==',
    '_ga': 'GA1.1.1539621866.1770884760',
    'feature_worten_life': 'true',
    'feature-loyalty-membership-v2': 'true',
    'feature_continente_consents': 'false',
    'feature_googlepay_provider': 'true',
    'feature-home-plan': 'true',
    'feature_applepay_provider_v2': 'true',
    'feature-pub-store-electronic-invoice-hestia': 'true',
    'FPID': 'FPID2.2.8xDh2MnHu%2BTn0%2Fi2ecjqFdds2L3e%2BbWvpLeCnLlBky8%3D.1770884760',
    'h2h-cookie': 'A',
    'kk_leadtag': 'true',
    '_pin_unauth': 'dWlkPU1HVXdPREkzTVRNdE1qQTVNQzAwWXpObUxXSXdaVEV0Wm1Oa01qRTNaR1k0TjJJeA',
    'mirakl-ads-uuid': '8a98a5b0-e26f-43c6-8d40-8c703559e478',
    '_fbp': 'fb.1.1770897863602.277121509794651427',
    '_tt_enable_cookie': '1',
    '_ttp': '01KH8VSX55ZP27VC8MG7JVXSMT_.tt.1',
    'FPLC': 'C7H8%2FKRU6ajBOLm1hZIAqvPEDMZ28NPHc9mdVRzNopnPyKxuONp56rhr2ciSx6K5gctIb3Vdz4L6O0G50DWVNq2H%2FYcegA5L4Vm3mepe4MnWnxbu5PpA73Nv%2FPcvkw%3D%3D',
    'cf_clearance': '4oP2HUw5gDQIgSDJMc.7hkE7c.t_qmYfM9IaPh64nM4-1771318045-1.2.1.1-pe00H_oZBcLvx5BsMjJlS9Bud.W9I0Gfeg0FcQ3k3iITBHBkHEd.cDRjP0ZvumgLLE1Rgop7ar6AKEwVtxgSTpSCH20nLg9YTflvnZWxvnMWAZGslMgMPHB7vZOC6KQAaho3RmBCY3bhjGrBbA9WfXk_f8jijqEvqAhO6HJo0s59fT8nqMa4KUpwHdzi1AyqY3IwCdHvf61yVYkVlcl_1RHMr9KViOn4j5Spw2coMFE',
    '_rdt_uuid': '1770897863216.f13b3535-eed0-41ca-9bc4-c0d8c822a6c4',
    '_rdt_em': ':21348728070e9d603508aac52c1e54ecc92283c29ab251078d618c3914e3ac7d,d08fdd1612736e5fb2561a7fa651e5003b3ae4034e0cf7bf039f16648ba914d5,a3f78f09875516d343e35d8174b099897f8aa0aaeda06885f883a40b2d58977f',
    'tfpsi': '9b9d2bef-07f9-4e2b-a5ec-21f0b5a9de2e',
    '_hjSession_1680786': 'eyJpZCI6ImUzOWQ1OGRhLTgwYmItNDM0Ny1hYzM4LWI3MzA1YzZkMTRhMyIsImMiOjE3NzEzMTgwNDg4MTIsInMiOjEsInIiOjEsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=',
    'rr_rcs': 'eF5jYSlN9jA0TbQwNDM21jVLNjHXNUlMS9M1MTA01zW3MDM3NDFOMk8xSOXKLSvJTBEwNDSy0DXUNQQAf7ENpg',
    '__rtbh.uid': '%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22%22%2C%22expiryDate%22%3A%222027-02-17T08%3A47%3A33.465Z%22%7D',
    'ttcsid': '1771318048011::QbK-8Qhb_H2YXUjIzYaT.7.1771318058044.0',
    'ttcsid_C5JHC7VGE0M3SF4JSP00': '1771318048010::mdrBtUgLnjFRMpWd0dX9.7.1771318058049.1',
    'rr_rcs': 'eF5jYSlN9jA0TbQwNDM21jVLNjHXNUlMS9M1MTA01zW3MDM3NDFOMk8xSOXKLSvJTBEwNDSy0DXUNQQAf7ENpg',
    '__rtbh.lid': '%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22aW2bxITm1almMF5jpGfa%22%2C%22expiryDate%22%3A%222027-02-17T08%3A49%3A46.935Z%22%7D',
    '_ga_WM5ETPQSYP': 'GS2.1.s1771318047$o13$g1$t1771318188$j57$l0$h0',
    '_ga_780GS19BPN': 'GS2.1.s1771318047$o13$g1$t1771318188$j57$l0$h633469307',
    'g_state': '{"i_l":0,"i_ll":1771318189587,"i_b":"A9hnmOKaUyl6ZYz8YUtG18H/iEk7y8Eh5fC9S5tCAgM","i_e":{"enable_itp_optimization":0}}',
    'cto_bundle': 'JXO2AF9uSTNtRWpkaFVqejN1OVFvZ1Z3UTA1eEFvdUxBQ2ZoRWpZY0VvdlVjYXNac09RQjhWSHpRb2l2ekFiNyUyRlh4bjFzbG1lRTRKdXMwUHA0RWdHTWNsenJvWWFMTyUyQmEyY2pVJTJGalRFQ2RGQ283JTJCUEYxVmZVTVliNGhDSHpmZU9OSDhmWTVETGozUHoxWHVFbGFwajl1SGVNZyUzRCUzRA',
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
