
import time
import traceback

from src.core.browser import CDPBrowser
from src.services.telegram import TelegramNotifier, TelegramErrorBot
from src.parsers.upwork_job_detail import UpworkJobDetailParser
from src.storage.daily_storage import DailyStorage
from src.storage.global_storage import GlobalStorage
from src.utils.human_actions import HumanActions

from src.loaders.account_loader import load_accounts
from src.loaders.keywork_loader import load_keywords_for_account

from src.actions.actions import back_to_homepage, reopen_tab, chose_dropdown_filter

from src.crawler import crawl_jobs


from src.filters.get_uncrawled_jobs import filter_unseen_jobs
from src.flow.random_workflow import strategy_home_direct
from src.parsers.telegram_message_parser import format_job_message
from src.core.network import wait_for_internet
from src.utils.dom_checked import can_interact, is_in_viewport, wait_until_loaded

def main():
    try:
        accounts = load_accounts()
        for account in accounts:
            keyworks = load_keywords_for_account(account['account_id'])
            account['keywords'] = keyworks

        global_storage = GlobalStorage()
        
        storage = DailyStorage(
            account="acc_01",
            platform="python_web"
        )

        keywords_acc = list(accounts[0].get("keywords"))

        tg = TelegramNotifier(token='8540621108:AAGr7mWnavHdgR5Ox5Sb-uY0vA1W5tHgxng', chat_id='5764023446')
        errBot = TelegramErrorBot(token='8299609180:AAEFs4UX5Hg4EjqArNybOruq66q3ks_8LIc', chat_id='5764023446')

        for keyobj in keywords_acc:
            key = dict(keyobj).get('keyword')
            storage.update_keyword_state(
                key,
                "WAITING",
            )
        
        browser = CDPBrowser()
        page = browser.connect()  

        human_actions = HumanActions(page)

        back_to_homepage(page)
        
        while True:
            try:
                print("🚀 Chuẩn bị chạy crawler")
                # 🌐 1. Đợi có mạng
                wait_for_internet()

                checkpoint = storage.load_keyword_checkpoint()
                
                keyword_state_to_crawl = [dict(x).get('keyword') for x in keywords_acc]
                keyword_to_crawl = []

                for keyword in keyword_state_to_crawl:
                    keyword_state = checkpoint.get(keyword)
                    if keyword_state["status"] == "WAITING" or keyword_state["status"] == "RUNNING":
                        keyword_to_crawl.append(keyword)

                if len(keyword_to_crawl) == 0:
                    keyword_to_crawl = keyword_state_to_crawl
                    for keyword in keyword_state_to_crawl:
                        storage.update_keyword_state(
                            key,
                            "WAITING",
                        )
                        

                storage.rotate_if_new_day()
                # and can_interact(page.locator('[data-test="carousel-slide"]'))


                # Chờ trang chủ phản hồi
                condi = can_interact(page.locator('input[placeholder="Search for jobs"]')) is False or can_interact(page.locator('[data-test="carousel-slide"]')) is False
                if not wait_until_loaded(lambda: condi, timeout=60, interval=5, mess="⏳Chờ trang chủ phản hồi..."):
                    raise Exception("Không load được trang chủ!")

                # ▶️ 2. Chạy crawler chính
                for key in keyword_to_crawl:

                    info = checkpoint.get(key)

                    if info:
                        if info["status"] == "FAILED" and info.get("retry", 0) >= 3:
                            continue
                    

                    storage.update_keyword_state(
                        key,
                        "RUNNING",
                    )
                    print(f"✔ Bắt đầu scrawling keyword: {key}")

                    strategy_home_direct(page, key) # Nhập keyword vào search input
                    
                    is_loaded = 'search' not in page.url or can_interact(page.locator('[aria-labelledby="jobs-sort-dropdown"]')) is False
                    if not wait_until_loaded(lambda: is_loaded, timeout=30, interval=5, mess="⏳Chờ trang search phản hồi!"):
                        raise Exception("Không load được trang tìm kiếm!")

                    chose_dropdown_filter(page)

                    page.wait_for_timeout(5000)

                    job_list = crawl_jobs(page)

                    jobs_to_click = filter_unseen_jobs(jobs=job_list, storage=storage, max_posted_age_minutes=180)
                    

                    print(f"🔍 Có {len(jobs_to_click)} job mới cần thu thập")

                    crawled_jobs = []

                    for job in jobs_to_click:
                        print(f"🕷 Đang thu thập dữ liệu job: {job['job_id']}")

                        job_locator = page.locator(f"article[data-ev-job-uid='{job['job_id']}']")

                        job_locator.scroll_into_view_if_needed()

                        while '/details/' not in page.url:
                            human_actions.human_click(job_locator)
                            time.sleep(5)
                        
                        
                        while can_interact(page.locator('[class="job-details-content"]')) is False:
                            print("Đang chờ job detail")
                            time.sleep(5)
                        
                        job_parser = UpworkJobDetailParser(page.get_by_role("dialog").inner_html())
                        
                        job_detail = job_parser.to_dict()

                        if job_detail:
                            crawled_jobs.append(job_detail)
                            print(f"Đã thu thấp thành công!")
                            storage.mark_job_seen(job_detail["job_id"])
                            tg.send(format_job_message(job_detail))
                            
                            print(f"💾 Đã lưu vào cở sử dữ liệu")
                            storage.save_jobs([job_detail])

                        # human_smooth_scroll(page)

                        page.wait_for_timeout(5000)
                        
                        previus_button_locator = page.locator('div[data-test="JobDetailsSliderHeader"]>button')

                        if can_interact(previus_button_locator):
                            human_actions.human_click(previus_button_locator)

                        while previus_button_locator.count() > 0:
                            time.sleep(1)

                    storage.update_keyword_state(
                        key,
                        "DONE",
                    )

                    print(f"🚀 Đã thu thập được tổng cộng {len(crawled_jobs)}")

                    back_to_homepage(page)

                global_storage.log_history_if_needed(
                    account=storage.account,
                    platform=storage.platform,
                    total_jobs=len(storage.load_jobs()),
                )               

                print("✅ Crawl xong 1 vòng – nghỉ 10 phút")

                time.sleep(600)

            except Exception as e:
                errBot.error(err=e, context="Main loop")
                print("💥 Lỗi không mong muốn, restart sau 30s")
                global_storage.log_error(
                    account=storage.account,
                    platform=storage.platform,
                    stage="search",
                    error=e,
                )
                if e is TimeoutError:
                    page = reopen_tab(page)
                back_to_homepage(page)
                traceback.print_exc()
                time.sleep(5)
                
        
        
        
    except Exception as e:
        errBot.error(e)
        print(e)
    finally:
        browser.close()
    

if __name__ == "__main__":
    main()