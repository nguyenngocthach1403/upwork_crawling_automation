from datetime import datetime
from .file_io import append_csv
from .paths import StoragePaths
from datetime import date
import csv


class GlobalStorage:
    def __init__(self, base_dir="output"):
        self.paths = StoragePaths(base_dir)

    # ------------------------
    # Crawl history
    # ------------------------
    def log_history(
        self,
        *,
        date: str,
        account: str,
        platform: str,
        total_jobs: int,
    ):
        append_csv(
            self.paths.crawl_history(),
            {
                "date": date,
                "account": account,
                "platform": platform,
                "total_jobs": total_jobs,
            }
        )

    # ------------------------
    # Error log
    # ------------------------
    def log_error(
        self,
        *,
        account: str,
        platform: str,
        error: Exception | str,
        keyword: str | None = None,
        stage: str = "unknown",
    ):
        if isinstance(error, Exception):
            error_type = type(error).__name__
            error_message = str(error)
        else:
            error_type = "Error"
            error_message = error

        append_csv(
            self.paths.error_log(),
            {
                "timestamp": datetime.now().isoformat(),
                "account": account,
                "platform": platform,
                "keyword": keyword or "",
                "stage": stage,
                "error_type": error_type,
                "error_message": error_message,
            }
        )
        
    def log_history_if_needed(
        self,
        *,
        account: str,
        platform: str,
        total_jobs: int,
        crawl_date: str | None = None,
    ):
        crawl_date = crawl_date or date.today().isoformat()
        path = self.paths.crawl_history()

        # Nếu file chưa tồn tại → ghi luôn
        if not path.exists():
            append_csv(path, {
                "date": crawl_date,
                "account": account,
                "platform": platform,
                "total_jobs": total_jobs,
            })
            return True

        # Check đã ghi chưa
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if (
                    row["date"] == crawl_date
                    and row["account"] == account
                    and row["platform"] == platform
                ):
                    return False  # đã ghi rồi

        # Chưa ghi → append
        append_csv(path, {
            "date": crawl_date,
            "account": account,
            "platform": platform,
            "total_jobs": total_jobs,
        })
        return True
