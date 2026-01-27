class CategoryManager:

    def crawl_categories(self, crawler, start_url, breadcrumb):
        page = crawler.open(start_url)
        page.wait_for_load_state("networkidle")

        end_categories = []

        
        links = page.eval_on_selector_all(
            'a[href^="/collections/"]',
            """els => els.map(e => ({
                name: e.innerText.trim(),
                url: e.href
            }))"""
        )

        
        seen = set()
        clean_links = []

        for link in links:
            name = link["name"]
            url = link["url"]

            if not name or name.lower() == "view all":
                continue

            if url in seen:
                continue

            seen.add(url)
            clean_links.append(link)

        
        if not clean_links:
            return [{
                "breadcrumb": breadcrumb,
                "url": start_url
            }]

        
        for link in clean_links:
            new_breadcrumb = breadcrumb + [link["name"]]

            sub_page = crawler.open(link["url"])
            sub_page.wait_for_load_state("networkidle")

            products = sub_page.query_selector_all('a[href*="/products/"]')

            if products:
                end_categories.append({
                    "breadcrumb": new_breadcrumb,
                    "url": link["url"]
                })
            else:
                end_categories.extend(
                    self.crawl_categories(
                        crawler,
                        link["url"],
                        new_breadcrumb
                    )
                )

        return end_categories
