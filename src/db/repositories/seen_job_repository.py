from datetime import date
from .base_repository import BaseRepository


class SeenJobRepository(BaseRepository):

    def __init__(self, database):
        super().__init__(database)

    def initialize(self):
        self.execute("""
        CREATE TABLE IF NOT EXISTS seen_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE NOT NULL,
            seen_date DATE NOT NULL
        )
        """)

    def mark_seen(self, job_id: str):
        today = date.today().isoformat()

        self.execute("""
        INSERT OR IGNORE INTO seen_jobs (job_id, seen_date)
        VALUES (?, ?)
        """, (job_id, today))

    def is_seen(self, job_id: str) -> bool:
        row = self.fetch_one(
            "SELECT 1 FROM seen_jobs WHERE job_id = ?",
            (job_id,)
        )
        return row is not None

    def filter_unseen(self, job_ids: list[str]) -> list[str]:
        unseen = []
        for job_id in job_ids:
            if not self.is_seen(job_id):
                unseen.append(job_id)
        return unseen
    
    def count(self) -> int:
        row = self.fetch_one("SELECT COUNT(*) as total FROM seen_jobs")
        return row["total"]

