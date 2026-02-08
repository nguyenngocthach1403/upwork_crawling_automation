from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright


class CDPBrowser:
    def __init__(self, cdp_url="http://localhost:9222"):
        self.cdp_url = cdp_url
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def connect(self):
        self.playwright = sync_playwright().start()

        # Kết nối tới Chrome thật
        self.browser = self.playwright.chromium.connect_over_cdp(
            self.cdp_url
        )

        # Chrome thường chỉ có 1 context
        self.context = self.browser.contexts[0]

        # Lấy page đang mở hoặc tạo mới
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()

        return self.page

    def new_page(self):
        self.page = self.context.new_page()
        return self.page

    def close(self):
        # KHÔNG close Chrome
        if self.playwright:
            self.playwright.stop()
