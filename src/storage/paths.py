from pathlib import Path


class StoragePaths:
    def __init__(self, base_dir="output"):
        self.base = Path(base_dir)

    def day_dir(self, account, keyword, date):
        return self.base / account / keyword / date

    def jobs(self, account, keyword, date):
        return self.day_dir(account, keyword, date) / "jobs.json"

    def seen_jobs(self, account, keyword, date):
        return self.day_dir(account, keyword, date) / "seen_jobs.json"

    def state(self, account, keyword, date):
        return self.day_dir(account, keyword, date) / "state.json"

    def crawl_log(self, account, keyword, date):
        return self.day_dir(account, keyword, date) / "crawl_log.csv"

    def latest(self, account, keyword):
        return self.base / account / keyword / "latest.json"

    def crawl_history(self):
        return self.base / "_global" / "crawl_history.csv"

    def error_log(self) -> Path:
        path = self.base / "_global" / "error_log.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    
    def keyword_checkpoint(self, account, platform, crawl_date):
        return (self.day_dir(account, platform, crawl_date) / "keyword_checkpoint.json")
