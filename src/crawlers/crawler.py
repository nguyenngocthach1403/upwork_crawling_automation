
import time
from src.parsers.upwork_jobs_parser import JobListParser
from src.parsers.upwork_job_detail import UpworkJobDetailParser
from src.core.browser import CDPBrowser
from src.utils.human_actions import HumanActions
from src.storage.daily_storage import DailyStorage
from src.services.telegram import TelegramErrorBot, TelegramNotifier
from src.storage.global_storage import GlobalStorage
from src.db.database_manager import DatabaseManager
from src.models import Job
# ================
# Function
# ================
from src.actions.actions import back_to_homepage, chose_dropdown_filter, reopen_tab
from src.actions.search import strategy_home_direct
from src.core.network import wait_for_internet
from src.utils.dom_checked import can_interact, wait_until_loaded, wait_for_action, is_in_viewport


class CrawlerMainLoop:
    def __init__(self, account, db_manager: DatabaseManager):
        self.account = account
        self.db = db_manager

        self.job_repo = db_manager.job_repo
        self.seen_repo = db_manager.seen_repo
        self.session_repo = db_manager.crawl_session_repo

        self.browser = CDPBrowser()
        self.page = self.browser.connect()
        self.human_actions = HumanActions(self.page)

        self.storage = DailyStorage(
            account=self.account['account_id'],
            platform="python_web"
        )

        self.notifier = TelegramNotifier(token='8540621108:AAGr7mWnavHdgR5Ox5Sb-uY0vA1W5tHgxng', chat_id='-5060223784')
        self.global_storage = GlobalStorage()

    def load_account_keywords(self):
        account_keywords = [item['keyword'] for item in self.account["keywords"]]
        return account_keywords

    def load_checkpoint(self):
        checkpoint = self.storage.load_keyword_checkpoint()
                
        account_keywords = self.load_account_keywords()
        keyword_to_crawl = []

        for keyword in account_keywords:
            keyword_state = checkpoint.get(keyword)
            if keyword_state["status"] == "WAITING" or keyword_state["status"] == "RUNNING":
                keyword_to_crawl.append(keyword)

        if len(keyword_to_crawl) == 0:
            keyword_to_crawl = account_keywords
            for keyword in account_keywords:
                self.storage.update_keyword_state(
                    keyword,
                    "WAITING",
                )
        return keyword_to_crawl

    def crawling_keywords(self):
        for keyword in self.load_account_keywords():

            session_id = self.session_repo.start(
                keyword=keyword,
                account=self.account["account_id"]
            )

            total_jobs = 0
            new_jobs = 0

            try:
                self.storage.update_keyword_state(keyword, "RUNNING")

                print(f"✔ Bắt đầu crawling keyword: {keyword}")
                time.sleep(1)
                strategy_home_direct(self.page, keyword)

                is_loaded = 'search' not in self.page.url or can_interact(self.page.locator('[aria-labelledby="jobs-sort-dropdown"]')) is False
                if not wait_until_loaded(lambda: is_loaded, timeout=30, interval=5, mess="⏳Chờ trang search phản hồi!"):
                    raise Exception("Không load được trang tìm kiếm!")
                
                chose_dropdown_filter(self.page)
                self.page.wait_for_timeout(5000)

                joblist_parser = JobListParser(self.page.content())
                job_list = joblist_parser.parse()

                total_jobs = len(job_list)

                jobs_to_click = self.seen_repo.filter_unseen(
                    [job["job_id"] for job in job_list]
                )
                print(f"🔍 Có {len(jobs_to_click)} job mới cần thu thập")
                for job_id in jobs_to_click:
                    print(f"🕷 Đang thu thập dữ liệu job: {job_id}")
                    job_detail = self.collect_job_detail(job_id)

                    if job_detail:
                        self.job_repo.upsert(Job.from_dict(job_detail))
                        self.seen_repo.mark_seen(job_detail["job_id"])
                        print(f"Đã thu thấp thành công!")
                        self.notifier.send(job_detail)
                        print(f"💾 Đã lưu vào cở sử dữ liệu")
                        new_jobs += 1

                self.session_repo.finish(
                    session_id=session_id,
                    total_jobs=total_jobs,
                    new_jobs=new_jobs,
                    status="success"
                )
                self.storage.update_keyword_state(
                    keyword,
                    "DONE",
                )
                self.human_actions._human_sleep(5, 10)
                print(f"🚀 Đã thu thập được tổng cộng {new_jobs}")
                back_to_homepage(self.page)

            except Exception as e:

                self.session_repo.finish(
                    session_id=session_id,
                    total_jobs=total_jobs,
                    new_jobs=new_jobs,
                    status="failed",
                    error=str(e)
                )

                raise

    def collect_job_detail(self, job_id):
        job_locator = self.page.locator(
            f"article[data-ev-job-uid='{job_id}']"
        )

        while not is_in_viewport(job_locator):
            job_locator.scroll_into_view_if_needed()
            self.page.wait_for_timeout(timeout=3000)

        while '/details/' not in self.page.url:
            # self.human_actions.human_click(job_locator)
            job_locator.click()
        
        
        if not wait_until_loaded(lambda: can_interact(self.page.locator('[class="job-details-content"]')),interval=5, timeout=30, mess="Đang chờ job detail"):
            print("Không load được job!")
            return

        job_parser = UpworkJobDetailParser(
            self.page.get_by_role("dialog").inner_html()
        )

        job_detail = job_parser.to_dict()

        self.page.wait_for_timeout(5000)

        self.page.go_back()
        
        self.human_actions._human_sleep(5, 10)

        return job_detail
    
    def crawling_loop(self):

        while True:
            session_id = None

            try:
                wait_for_internet()

                # Start global crawl session
                session_id = self.session_repo.start(
                    keyword="ALL",
                    account=self.account["account_id"]
                )

                print("🚀 Bắt đầu 1 vòng crawl mới")

                back_to_homepage(self.page)

                self.storage.rotate_if_new_day()

                self.crawling_keywords()

                total_jobs = len(self.storage.load_jobs())

                self.global_storage.log_history_if_needed(
                    account=self.storage.account,
                    platform=self.storage.platform,
                    total_jobs=total_jobs,
                )

                self.session_repo.finish(
                    session_id=session_id,
                    total_jobs=total_jobs,
                    new_jobs=0,  # hoặc bạn tính riêng nếu muốn
                    status="success"
                )

                print("✅ Crawl xong 1 vòng – nghỉ 10 phút")
                time.sleep(600)

            except Exception as e:

                print("💥 Lỗi không mong muốn:", e)

                if session_id:
                    self.session_repo.finish(
                        session_id=session_id,
                        total_jobs=0,
                        new_jobs=0,
                        status="failed",
                        error=str(e)
                    )

                errBot = TelegramErrorBot(
                    token='xxx',
                    chat_id='xxx'
                )

                errBot.error(err=e, context="Main loop")

                self.global_storage.log_error(
                    account=self.storage.account,
                    platform=self.storage.platform,
                    stage="main_loop",
                    error=e,
                )

                try:
                    self.page = reopen_tab(self.page)
                except Exception:
                    print("⚠ Không reopen được tab")

                print("⏳ Restart sau 30s")
                time.sleep(30)

