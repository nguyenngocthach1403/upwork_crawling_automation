import requests
import time
import traceback
from src.parsers.budget_text import budget_text
import socket
TOKEN = ""
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        # Sử dụng trực tiếp đối tượng bot từ thư viện telebot
        self.bot = telebot.TeleBot(token)
        self.chat_id = chat_id

    def send(self, job: dict):
        # Tạo bàn phím Inline chuyên nghiệp
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
            text="View on Upwork 🫧", 
            url=job.get('url', '#')
        ))
        
        # Gửi qua phương thức của telebot để tối ưu hiệu suất
        self.bot.send_message(
            self.chat_id, 
            self.format_job_message(job), 
            parse_mode="HTML", 
            reply_markup=markup,
            disable_web_page_preview=False
        )
        
    def format_job_message(self, job: dict) -> str:
        # Hàm hỗ trợ lấy budget (giả định bạn đã có hàm budget_text bên ngoài)

        title = job.get('title', 'No title').upper() # Viết hoa tiêu đề cho nổi bật
        posted = job.get('posted_text', 'N/A')
        budget = budget_text(job)
        skills = ", ".join(job.get('skills', [])) if job.get('skills') else 'N/A'
        location = job.get('location', 'Worldwide')
        
        activities = job.get('activities', {})
        proposals = activities.get('proposals', 'N/A')
        invites = activities.get('invites_sent', 'N/A')
        hires = activities.get('invites_sent', 'N/A') if activities.get('invites_sent', 'N/A') else 'N/A'
        
        client = job.get('client', {})
        rating = client.get('rating', 'N/A')
        hire_rate = client.get('hire_rate', 'N/A') 
        posted_jobs = client.get('posted_jobs', 'N/A')
        url = job.get('url', '#')

        # Sử dụng thẻ <code> để các con số/ID dễ copy hơn
        return (
            f"🔔 <b>NEW JOB</b> 🔔 Posted:<i>{posted}</i>\n\n"
            f"   <strong>{title}</strong>\n"
            f"💵 <b>Budget:</b> <code>{budget}</code>\n"
            f"📍 <b>Location:</b> {location}\n"
            f"🛠 <b>Skills:</b> <i>{skills}</i>\n"
            f"📊 <b>Proposals:</b> {proposals}\n"
            f"⚡ <b>Invites:</b> {invites}\n"
            f"⚡ <b>Hires:</b> {hires}\n"
            f"👤 <b>CLIENT INFO</b>\n"
            f"• <b>Rating:</b> <i>{str(rating).strip()}</i>\n"
            # f"• <b>Feedback:</b> <i>{rating[1].strip()}</i>\n"
            f"• <b>Hire rate:</b> <i>{hire_rate}</i>\n"
            f"• <b>Total jobs:</b> <i>{posted_jobs}</i>\n"
        ).strip()

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