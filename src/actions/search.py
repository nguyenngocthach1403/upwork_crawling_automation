import random
from src.utils.human_actions import HumanActions
from src.utils.dom_checked import can_interact, is_in_viewport, wait_for_action, wait_until_loaded

def strategy_home_direct(page, keyword):
    human_action = HumanActions(page)

    # 1. Type ở homepage
    search_locator = page.locator('[placeholder="Search for jobs"]')
    if not can_interact(search_locator):
        raise Exception("Không tìm thấy search input để nhập từ khóa")

    while is_in_viewport(search_locator) is False:
        search_locator.scroll_into_view_if_needed()

    if is_in_viewport(search_locator) is False:
        raise Exception("Không tìm thấy search input để nhập từ khóa")
    
    # if not wait_for_action(lambda: {search_locator.get_attribute('aria-expanded') == 'true'}, human_action.human_click(search_locator), timeout=30, interval=5):
    #     raise Exception("Không tìm thấy search input để nhập từ khóa")
    human_action.human_click(search_locator)
    human_action._human_sleep(0.2, 0.5)
    human_action.human_type(keyword)
    human_action._human_sleep(0.2, 0.5)

    page.keyboard.press("Enter")


def strategy_find_work(page, keyword):
    human_action = HumanActions(page)

    # 2. Click Find work -> search page -> type
    find_work = 'button[id="caret-btn-findWorkHome"]'
    find_work_locator = page.locator(find_work)
    human_action.move_mouse_to_locator(find_work_locator)
    human_action._human_sleep()
    find_work_link = 'ul[data-cy="dropdown-menu"] li[class="active active"]'
    find_work_link_locator = page.locator(find_work_link)
    human_action._human_sleep()

    human_action.human_click(page, find_work_link_locator)
    strategy_home_direct(page, keyword)


    


def strategy_recent_search(page, keyword):
    human_action = HumanActions(page)
    # 3. Click search input -> recent search
    search_input = '[placeholder="Search for jobs"]'

    search_input_locator = page.locator(search_input)

    human_action.human_click(page, search_input_locator)

    human_action._human_sleep()

    recent_items = page.locator('div[data-test="menu-container"] li')

    if recent_items.count() > 0:
        idx = random.randint(0, recent_items.count() - 1)
        human_action.human_click(page, recent_items.nth(idx))
    
    human_action._human_sleep(min_s=4, max_s=5)
    page.wait_for_load_state("networkidle")
    # Sau khi sang trang search → nhập keyword mới
    human_action._human_sleep()
    search_input_locator = page.locator('input[aria-labelledby="search-bar-label"]')
    human_action.human_click(page, search_input_locator)
    human_action._human_sleep()
    page.keyboard.press('Control+A')
    human_action._human_sleep()
    page.keyboard.press('Backspace')
    human_action._human_sleep()
    human_action.human_type(page, keyword)
    human_action._human_sleep()
    page.keyboard.press('Enter')
