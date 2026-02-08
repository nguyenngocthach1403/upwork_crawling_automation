import json
import csv
from datetime import date, datetime
from pathlib import Path
from .paths import StoragePaths


class DailyStorage:
    def __init__(
        self,
        account: str,
        platform: str,
        crawl_date: str | None = None,
        paths: StoragePaths | None = None
    ):
        self.account = account
        self.platform = platform
        self.crawl_date = crawl_date or date.today().isoformat()
        self.paths = paths or StoragePaths()

        # ---- Resolve paths ----
        self.day_dir = self.paths.day_dir(
            self.account, self.platform, self.crawl_date
        )

        self.jobs_file = self.paths.jobs(
            self.account, self.platform, self.crawl_date
        )
        self.seen_jobs_file = self.paths.seen_jobs(
            self.account, self.platform, self.crawl_date
        )
        self.state_file = self.paths.state(
            self.account, self.platform, self.crawl_date
        )
        self.crawl_log_file = self.paths.crawl_log(
            self.account, self.platform, self.crawl_date
        )

        self.latest_file = self.paths.latest(
            self.account, self.platform
        )
        self.global_history_file = self.paths.crawl_history()
        
        self.keyword_checkpoint_file = self.paths.keyword_checkpoint(
            self.account, self.platform, self.crawl_date
        )


        self._ensure_structure()

    # ------------------------
    # Init & helpers
    # ------------------------
    def _ensure_structure(self):
        self.day_dir.mkdir(parents=True, exist_ok=True)
        self.latest_file.parent.mkdir(parents=True, exist_ok=True)
        self.global_history_file.parent.mkdir(parents=True, exist_ok=True)

        self._ensure_json(self.jobs_file, [])
        self._ensure_json(self.seen_jobs_file, [])
        self._ensure_json(self.state_file, {})
        self._ensure_json(self.keyword_checkpoint_file, {})
        self._ensure_csv(self.crawl_log_file, ["timestamp", "action", "value"])
        self._ensure_csv(
            self.global_history_file,
            ["date", "account", "platform", "total_jobs"]
        )

    def _ensure_json(self, path: Path, default):
        if not path.exists():
            path.write_text(
                json.dumps(default, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

    def _ensure_csv(self, path: Path, headers: list[str]):
        if not path.exists():
            with open(path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(headers)

    def _read_json(self, path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, data):
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
    def rotate_if_new_day(self) -> bool:
        """
        Check nếu sang ngày mới thì:
        - update crawl_date
        - resolve lại toàn bộ path
        - ensure structure mới
        """
        today = date.today().isoformat()

        if today == self.crawl_date:
            return False  # chưa sang ngày mới

        # ---- rotate ----
        self.crawl_date = today

        self.day_dir = self.paths.day_dir(
            self.account, self.platform, self.crawl_date
        )

        self.jobs_file = self.paths.jobs(
            self.account, self.platform, self.crawl_date
        )
        self.seen_jobs_file = self.paths.seen_jobs(
            self.account, self.platform, self.crawl_date
        )
        self.state_file = self.paths.state(
            self.account, self.platform, self.crawl_date
        )
        self.crawl_log_file = self.paths.crawl_log(
            self.account, self.platform, self.crawl_date
        )

        # nếu có keyword checkpoint theo ngày
        self.keyword_checkpoint_file = self.paths.keyword_checkpoint(
            self.account, self.platform, self.crawl_date
        )

        # tạo file/folder mới
        self._ensure_structure()

        return True
    # ------------------------
    # Jobs
    # ------------------------
    def save_jobs(self, new_jobs: list[dict], key: str = "job_id"):
        """
        Merge jobs theo job_id
        - job mới -> thêm
        - job cũ -> giữ hoặc update
        """

        # Load existing jobs
        try:
            existing_jobs = self.load_jobs()
        except Exception:
            existing_jobs = []

        # Index theo job_id
        job_map: dict[str, dict] = {
            job[key]: job
            for job in existing_jobs
            if key in job
        }

        added = 0
        updated = 0

        for job in new_jobs:
            job_id = job.get(key)
            if not job_id:
                continue

            if job_id in job_map:
                # update nếu cần
                job_map[job_id].update(job)
                updated += 1
            else:
                job_map[job_id] = job
                added += 1

        merged_jobs = list(job_map.values())

        # Ghi full jobs trong ngày
        self._write_json(self.jobs_file, merged_jobs)

        # latest = lần crawl gần nhất
        self._write_json(self.latest_file, new_jobs)

        self.log_action("save_jobs", f"+{added} new, ~{updated} updated")

    # ------------------------
    # Checkpoint
    # ------------------------
    # ------------------------
    # Keyword checkpoint
    # ------------------------
    def load_keyword_checkpoint(self) -> dict:
        return self._read_json(self.keyword_checkpoint_file)

    def update_keyword_state(
        self,
        keyword: str,
        status: str,
        error: str | None = None,
        inc_retry: bool = False
    ):
        data = self.load_keyword_checkpoint()

        kw = data.get(keyword, {
            "status": "PENDING",
            "retry": 0
        })

        kw["status"] = status
        kw["updated_at"] = datetime.now().isoformat()

        if inc_retry:
            kw["retry"] = kw.get("retry", 0) + 1

        if error:
            kw["last_error"] = error

        data[keyword] = kw
        self._write_json(self.keyword_checkpoint_file, data)



    def load_jobs(self) -> list[dict]:
        return self._read_json(self.jobs_file)

    # ------------------------
    # Seen jobs
    # ------------------------
    def get_seen_job_ids(self) -> set[str]:
        return set(self._read_json(self.seen_jobs_file))

    def mark_job_seen(self, job_id: str):
        seen = self.get_seen_job_ids()
        if job_id not in seen:
            seen.add(job_id)
            self._write_json(self.seen_jobs_file, list(seen))

    # ------------------------
    # State
    # ------------------------
    def load_state(self) -> dict:
        return self._read_json(self.state_file)

    def update_state(self, **kwargs):
        state = self.load_state()
        state.update(kwargs)
        state["updated_at"] = datetime.now().isoformat()
        self._write_json(self.state_file, state)

    # ------------------------
    # Logs
    # ------------------------
    def log_action(self, action: str, value: str | int | float = ""):
        with open(self.crawl_log_file, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                datetime.now().isoformat(),
                action,
                value
            ])

    # ------------------------
    # Global crawl history
    # ------------------------
    def update_global_history(self, total_jobs: int):
        with open(self.global_history_file, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                self.crawl_date,
                self.account,
                self.platform,
                total_jobs
            ])
