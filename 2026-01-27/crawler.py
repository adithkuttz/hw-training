# crawler.py
from playwright.sync_api import sync_playwright

class WestsideCrawler:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()

    def open(self, url):
        page = self.context.new_page()
        page.goto(url, timeout=60000)
        return page

    def close(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()
