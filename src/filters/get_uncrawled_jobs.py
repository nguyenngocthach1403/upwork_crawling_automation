from typing import List, Dict
from src.storage.daily_storage import DailyStorage


def filter_unseen_jobs(
    jobs: List[Dict],
    storage: DailyStorage,
    max_posted_age_minutes: int | None = None
) -> List[Dict]:
    """
    Lọc ra các job CHƯA crawl

    jobs: danh sách job từ job list page
          mỗi job tối thiểu có:
          {
              "job_id": str,
              "posted_age_minutes": int (optional)
          }

    max_posted_age_minutes:
        nếu set → stop luôn khi gặp job quá cũ (dùng cho scroll)
    """

    seen_jobs = storage.get_seen_job_ids()
    crawled_jobs = storage.load_jobs()

    unseen_jobs = []

    for job in jobs:
        job_id = job.get("job_id")
        if not job_id:
            continue

        # ⛔ Stop scroll nếu job quá cũ
        if max_posted_age_minutes is not None:
            age = job.get("posted_age_minutes")
            if age is not None and age > max_posted_age_minutes:
                break

        # ⛔ Đã từng thấy trên list
        if job_id in seen_jobs:
            continue

        # ⛔ Đã crawl detail
        if job_id in crawled_jobs:
            continue
        
        unseen_jobs.append(job)

    return unseen_jobs
