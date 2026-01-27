import json
import time


class WestsideParser:

    
    def get_product_urls(self, page):
        return page.eval_on_selector_all(
            'a[href*="/products/"]',
            "els => [...new Set(els.map(e => e.href.split('?')[0]))]"
        )

    
    def get_product_json(self, page):
        scripts = page.locator('script[type="application/ld+json"]').all()
        for s in scripts:
            try:
                data = json.loads(s.inner_text())
                if data.get("@type") == "Product":
                    return data
            except:
                pass
        return {}

    def get_price(self, product_json):
        offers = product_json.get("offers", {})
        if isinstance(offers, dict):
            return offers.get("price", "")
        if isinstance(offers, list) and offers:
            return offers[0].get("price", "")
        return ""

    
    def get_details(self, page):
        details = {
            "net_quantity": "",
            "fit": "",
            "care_instruction": "",
            "fabric_composition": "",
            "country_of_origin": ""
        }

        try:
            
            header = page.locator("text=Product Details and Overview")
            if header.is_visible():
                header.click()
                time.sleep(0.5)  

            
            section = header.locator("xpath=ancestor::div[1]")
            text = section.inner_text()

            for line in text.split("\n"):
                line = line.strip()
                low = line.lower()

                if low.startswith("net quantity"):
                    details["net_quantity"] = line.split(":", 1)[-1].strip()

                elif low.startswith("care instruction"):
                    details["care_instruction"] = line.split(":", 1)[-1].strip()

                elif low.startswith("material"):
                    details["fabric_composition"] = line.split(":", 1)[-1].strip()

                elif low.startswith("country of origin"):
                    details["country_of_origin"] = line.split(":", 1)[-1].strip()

                elif low.startswith("fit"):
                    details["fit"] = line.split(":", 1)[-1].strip()

        except Exception:
            pass

        return details
