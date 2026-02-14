from datetime import date
from typing import List, Optional
from .base_repository import BaseRepository
from src.models.job_model import Job


class JobRepository(BaseRepository):

    def __init__(self, database):
        super().__init__(database)

    def initialize(self):
        self.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            posted_text TEXT,
            posted_minutes_ago INTEGER,
            location TEXT,
            description TEXT,
            job_type TEXT,
            budget TEXT,
            experience_level TEXT,
            skills TEXT,
            activities TEXT,
            client TEXT,
            url TEXT,
            crawled_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

    def upsert(self, job: Job):
        today = date.today().isoformat()

        self.execute("""
        INSERT INTO jobs (
            job_id, title, posted_text, posted_minutes_ago,
            location, description, job_type,
            budget, experience_level,
            skills, activities, client,
            url, crawled_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_id) DO UPDATE SET
            title=excluded.title,
            posted_text=excluded.posted_text,
            posted_minutes_ago=excluded.posted_minutes_ago,
            location=excluded.location,
            description=excluded.description,
            job_type=excluded.job_type,
            budget=excluded.budget,
            experience_level=excluded.experience_level,
            skills=excluded.skills,
            activities=excluded.activities,
            client=excluded.client,
            url=excluded.url,
            updated_at=CURRENT_TIMESTAMP
        """, job.to_db_tuple(today))

    def get_by_job_id(self, job_id: str) -> Optional[Job]:
        row = self.fetch_one(
            "SELECT * FROM jobs WHERE job_id = ?",
            (job_id,)
        )
        return Job.from_db_row(row) if row else None


    def count(self) -> int:
        row = self.fetch_one("SELECT COUNT(*) as total FROM jobs")
        return row["total"]

    def delete(self, job_id: str):
        self.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))

    def get_all(self):
        rows = self.fetch_all("SELECT * FROM jobs")
        return [Job.from_row(dict(row)) for row in rows]
