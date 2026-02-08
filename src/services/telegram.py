import requests
import time
import traceback
import socket

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    def send(self, text: str):
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        requests.post(self.url, json=payload, timeout=10)


class TelegramErrorBot:
    def __init__(self, token, chat_id, app_name="Crawler"):
        self.token = token
        self.chat_id = chat_id
        self.app_name = app_name
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.hostname = socket.gethostname()
        self.last_sent = 0

    def _send(self, text):
        requests.post(self.url, json={
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        })

    def error(self, err: Exception, context: str = ""):
        now = time.time()

        # anti spam: 1 lỗi / 10s
        if now - self.last_sent < 10:
            return
        self.last_sent = now

        trace = traceback.format_exc()

        msg = f"""
🚨 <b>{self.app_name} ERROR</b>

🖥 <b>Host:</b> {self.hostname}
📍 <b>Context:</b> {context}

❌ <b>Error:</b>
<pre>{str(err)}</pre>

📜 <b>Traceback:</b>
<pre>{trace[:3500]}</pre>
"""
        self._send(msg)