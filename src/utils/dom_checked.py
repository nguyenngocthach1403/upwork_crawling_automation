import time
def can_interact(locator):
    if locator.count() == 0:
        return False

    try:
        if not locator.is_visible():
            return False

        box = locator.bounding_box()
        if not box:
            return False

        return locator.evaluate("""
            el => {
                const s = getComputedStyle(el);
                return s.pointerEvents !== 'none' && !el.disabled;
            }
        """)
    except:
        return False
    
    
def is_in_viewport(locator) -> bool:
    try:
        return locator.evaluate("""
        (el) => {
            if (!el) return false;
            const r = el.getBoundingClientRect();
            return (
                r.bottom > 0 &&
                r.right > 0 &&
                r.top < window.innerHeight &&
                r.left < window.innerWidth
            );
        }
        """)
    except:
        return False
    
def wait_until_loaded(condition_func, timeout=15, interval=1, mess = "Wait..."):
    start = time.time()
    while time.time() - start < timeout:
        print(mess)
        if condition_func():
            print("✔️ Load trang thành công!")
            return True
        
        time.sleep(interval)
    return False


def wait_for_action(condition_func, action_func, timeout=15, interval=1, action_name = "action"):
    """
    wait_for_action: Hàm thực hiện các thao tác liên quan đến chuyển trang để đảm bảo ràng thao tác chuyển trang được thực hiện. 
    Khi thực hiện chuyển trang url sẽ thay đổi khi đó thao tác chuyển trang đã được thực hiện
    
    :param condition: Điều kiện để nhận biết thao đó đã thực hiện chưa.
    :param action_func: Tham số này là hàm dùng để thực hiện lại thao tác lại 1 lần nữa. Giảm nguy cơ thực hiện fail lần đầu.
    :param timeout: Giới hạn thời gian thực hiện thao tác để đảm bảo không bị mắc kẹt trong vòng lập vô hạn.
    :param interval: Thời gian nghỉ tránh thực hiện liên tục đủ thời gian để nhận định thao tác đã thực hiện.
    """
    start = time.time()
    while time.time() - start < timeout:
        action_func()               
        print(f"Đang thực hiện hành động {action_name}")
        time.sleep(interval)
        if condition_func():
            print(f"✔️ Thực hiện {action_name} thành công!")
            return True
        time.sleep(1)
    return False