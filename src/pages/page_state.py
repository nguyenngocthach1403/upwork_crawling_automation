
from .page_selectors import HomePageSelectors
from src.utils.dom_checked import wait_until_state, can_interact, is_in_viewport
class HomepageState:
    def __init__(self, page):
        self.selectors_str = HomePageSelectors()
        self.page = page
        
    
    def is_homepage(self):
        return wait_until_state(can_interact(self.page.locator('input[placeholder="Search for jobs"]')) is False and can_interact(self.page.locator('[data-test="carousel-slide"]')) is False, interval=1, mess="Wait for homepage loading!")
        