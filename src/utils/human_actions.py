import random
import math
import time

NEAR_KEYS = {
    "a": "sqwz",
    "s": "awedxz",
    "d": "serfcx",
    "f": "drtgvc",
    "g": "ftyhbv",
    "h": "gyujnb",
    "j": "huikmn",
    "k": "jiolm",
    "l": "kop",
}

class HumanActions:
    def __init__(self, page):
        self.page = page

    
    def _human_sleep(self, min_s=0.3, max_s=1.2):
        time.sleep(random.uniform(min_s, max_s))

    def human_move_mouse(self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        min_steps=25,
        max_steps=60,
        min_delay=0.005,
        max_delay=0.02,
        jitter=2,
        overshoot=True
    ):
        mouse = self.page.mouse

        # Số bước di chuyển
        steps = random.randint(min_steps, max_steps)

        # Overshoot nhẹ
        if overshoot:
            end_x += random.randint(-10, 10)
            end_y += random.randint(-10, 10)

        dx = end_x - start_x
        dy = end_y - start_y

        # Góc + độ cong
        curve = random.uniform(-0.3, 0.3)

        for i in range(steps + 1):
            t = i / steps

            # Ease in-out (chậm đầu – nhanh giữa – chậm cuối)
            ease = t * t * (3 - 2 * t)

            # Đường cong
            offset_x = math.sin(ease * math.pi) * curve * dx
            offset_y = math.sin(ease * math.pi) * curve * dy

            x = start_x + dx * ease + offset_x
            y = start_y + dy * ease + offset_y

            # Jitter
            x += random.uniform(-jitter, jitter)
            y += random.uniform(-jitter, jitter)

            mouse.move(x, y)
            time.sleep(random.uniform(min_delay, max_delay))

    def human_click(
        self,
        locator,
        hover=True,
        click_delay=(0.05, 0.25),
        min_steps=18,
        max_steps=30,
        offset_ratio=0.3
    ):
        """
        locator: Playwright locator
        hover: hover trước khi click
        offset_ratio: độ lệch tâm click (0.3 = 30% box)
        """

        box = locator.bounding_box()
        if not box:
            raise Exception("Cannot get bounding box")

        # vị trí click ngẫu nhiên trong box
        offset_x = random.uniform(
            box["width"] * offset_ratio * -1,
            box["width"] * offset_ratio
        )
        offset_y = random.uniform(
            box["height"] * offset_ratio * -1,
            box["height"] * offset_ratio
        )

        target_x = box["x"] + box["width"] / 2 + offset_x
        target_y = box["y"] + box["height"] / 2 + offset_y

        # vị trí chuột hiện tại (random nếu chưa có)
        start_x = random.randint(0, int(box["x"] + box["width"]))
        start_y = random.randint(0, int(box["y"] + box["height"]))

        self.human_move_mouse(
            start_x=start_x,
            start_y=start_y,
            end_x=int(target_x),
            end_y=int(target_y),
            min_steps=min_steps,
            max_steps=max_steps
        )

        if hover:
            self.page.mouse.move(target_x, target_y)
            self._human_sleep(min_s=0.2, max_s=0.6)

        time.sleep(random.uniform(*click_delay))
        self.page.mouse.down()
        time.sleep(random.uniform(0.03, 0.12))
        self.page.mouse.up()

        self._human_sleep()
    
    def move_mouse_to_locator(self, locator):
        box = locator.bounding_box()
        if not box:
            return

        target_x = box["x"] + box["width"] * random.uniform(0.3, 0.7)
        target_y = box["y"] + box["height"] * random.uniform(0.3, 0.7)

        # Điểm bắt đầu giả lập (chuột không teleport)
        start_x = random.randint(0, 300)
        start_y = random.randint(0, 300)

        self.human_move_mouse(
            start_x=start_x,
            start_y=start_y,
            end_x=int(target_x),
            end_y=int(target_y),
        )
    
    # ==============================
    # Typing
    # ==============================
    def human_type(
        self,
        text: str,
        typo_chance: float = 0.08,
        min_delay: float = 0.05,
        max_delay: float = 0.18,
    ):
        # text_len = len(text)

        for i, char in enumerate(text):
            # chỉ typo ở giữa, không typo đầu/cuối
            # allow_typo = (
            #     char.isalpha()
            #     and 0 < i < text_len - 1
            #     and random.random() < typo_chance
            # )

            # ❌ gõ sai
            # if allow_typo:
            #     wrong_pool = NEAR_KEYS.get(char.lower(), string.ascii_lowercase)
            #     wrong_char = random.choice(wrong_pool)

            #     page.keyboard.type(wrong_char)
            #     time.sleep(random.uniform(0.1, 0.12))
            #     page.keyboard.press("Backspace")
            #     time.sleep(random.uniform(0.1, 0.12))

            # ✅ gõ đúng
            self.page.keyboard.type(char)

            # delay giữa các phím
            self._human_sleep(min_delay, max_delay)

            # micro pause (người thật hay dừng rất ngắn)
            if random.random() < 0.04:
                self._human_sleep(0.3, 0.9)

        # pause sau khi gõ xong (rất quan trọng)
        self._human_sleep(0.4, 1.2)

