import time
from src.utils.dom_checked import can_interact, is_in_viewport, wait_for_action, wait_until_loaded
from src.utils.human_actions import HumanActions

def back_to_homepage(page):
    human_actions = HumanActions(page)
    home_locator = page.locator('[data-cy="brand"]')
    if can_interact(home_locator) is False:
        home_locator = page.locator('[class="nav-logo"]')
    if can_interact(home_locator) is False:
        raise Exception("Không tìm thấy Navigator trở về trang chủ!")   

        
    try:
        home_locator.scroll_into_view_if_needed(timeout=5000)
    except:
        page.go_back()

    
    if not wait_for_action(lambda: '/find-work/' in page.url, lambda:human_actions.human_click(home_locator), timeout=60, interval=5):
        raise Exception("Đã cố gắn nhưng không thể chuyển tra!")   

    is_loaded ='find-work' not in page.url or can_interact(page.locator('input[placeholder="Search for jobs"]')) is False or can_interact(page.locator('[data-test="carousel-slide"]')) is False
    if not wait_until_loaded(lambda: is_loaded, timeout=30, interval=5, mess="⏳Chờ load trang chủ!"):
        raise Exception("Không load được trang chủ!")

def chose_dropdown_filter(page):
    human_actions = HumanActions(page)
    filter_locator = page.locator('[aria-labelledby="jobs-sort-dropdown"]')
    filter_locator.scroll_into_view_if_needed()
    human_actions.human_click(filter_locator)
    page.wait_for_timeout(300)
    page.keyboard.press("Tab")
    page.keyboard.press("Enter")
    # if not wait_for_action(lambda: 'sort' in page.url, lambda: (), timeout=15, interval=1):
    #     raise Exception("Không load được most recent job!") 
    
    
    
    

    
def reopen_tab(page, url="https://www.upwork.com/nx/find-work/"):
    context = page.context

    print("🔄 Mở tab mới...")
    new_page = context.new_page()

    new_page.goto(url, timeout=30000)

    print("❌ Đóng tab cũ")
    try:
        page.close()
    except:
        pass

    return new_page


