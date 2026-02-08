import time
import random
import math

def should_scroll(probability=0.7):
    """
    probability: xác suất thực hiện scroll
    """
    return random.random() < probability

def human_smooth_scroll(
    page,
    total_distance=None,
    min_distance=1200,
    max_distance=3500,
    min_step=12,
    max_step=45,
    min_delay=0.008,
    max_delay=0.02
):
    """
    Scroll tốc độ người thật trên Upwork
    ~2–3s / 3000px
    """

    if total_distance is None:
        total_distance = random.randint(min_distance, max_distance)

    steps = random.randint(28, 55)
    current = 0

    for i in range(steps):
        progress = i / steps

        # easing nhẹ: đầu chậm – giữa nhanh – cuối chậm
        ease = 0.6 + 0.4 * math.sin(progress * math.pi)

        step = int(ease * random.randint(min_step, max_step))
        step = max(step, 8)

        if current + step > total_distance:
            step = total_distance - current

        page.mouse.wheel(0, step)
        current += step

        time.sleep(random.uniform(min_delay, max_delay))

        # pause giống đang quét mắt qua job
        if random.random() < 0.1:
            time.sleep(random.uniform(0.25, 0.7))

        if current >= total_distance:
            break


def human_scroll_up(page):
    steps = random.randint(5, 15)
    for _ in range(steps):
        page.mouse.wheel(0, -random.randint(2, 6))
        time.sleep(random.uniform(0.01, 0.03))


def human_scroll_flow(page):
    if not should_scroll(0.75):
        # Không scroll, chỉ đứng đọc
        time.sleep(random.uniform(1.0, 2.5))
        return

    human_smooth_scroll(page)

    # đôi khi scroll lên nhẹ
    if random.random() < 0.25:
        time.sleep(random.uniform(0.3, 0.8))
        human_scroll_up(page)


def human_scroll_to_locator(
    page,
    locator,
    max_scroll_rounds=5
):
    """
    Scroll như người thật đến khi locator nằm trong viewport
    """

    # 1️⃣ Không tồn tại trong DOM
    if locator.count() == 0:
        return False

    for _ in range(max_scroll_rounds):

        # 3️⃣ Lấy vị trí element
        box = locator.bounding_box()
        if not box:
            return False

        viewport_h = page.locator('div[class="layout"]').bounding_box()['height']

        # Vị trí Y tương đối của element so với viewport
        element_y = box["y"]
        scroll_y = page.evaluate("() => window.scrollY")

        # Khoảng cách cần scroll thêm
        distance = element_y - scroll_y - viewport_h * random.uniform(0.3, 0.5)

        # Nếu element nằm phía trên (scroll ngược)
        if distance < 0:
            page.mouse.wheel(0, int(distance))
            time.sleep(random.uniform(0.2, 0.4))
        else:
            # 4️⃣ Scroll xuống bằng human_smooth_scroll
            human_smooth_scroll(
                page,
                total_distance=int(distance)
            )

def scroll_to_top_like_human(page):
    current = page.evaluate("() => window.scrollY")
    if current <= 50:
        return

    steps = random.randint(4, 8)
    step = current // steps

    for _ in range(steps):
        page.mouse.wheel(0, -step)
        time.sleep(random.uniform(0.15, 0.35))
