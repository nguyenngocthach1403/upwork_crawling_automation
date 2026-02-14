from datetime import datetime, UTC
from typing import Optional

from .base_repository import BaseRepository
from src.models.crawl_session_model import CrawlSession


class CrawlSessionRepository(BaseRepository):

    def initialize(self):
        self.execute("""
            CREATE TABLE IF NOT EXISTS crawl_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                status TEXT NOT NULL,
                keyword TEXT,
                account TEXT,
                total_jobs INTEGER DEFAULT 0,
                new_jobs INTEGER DEFAULT 0,
                error TEXT
            )
        """)

    def start(self, keyword: str = None, account: str = None) -> int:
        started_at = datetime.now(UTC).isoformat()

        cursor = self.execute("""
            INSERT INTO crawl_sessions (
                started_at, status, keyword, account
            )
            VALUES (?, ?, ?, ?)
        """, (started_at, "running", keyword, account))

        return cursor.lastrowid

    def finish(
        self,
        session_id: int,
        total_jobs: int,
        new_jobs: int,
        status: str,
        error: str | None = None
    ):
        finished_at = datetime.now(UTC).isoformat()

        self.execute("""
            UPDATE crawl_sessions
            SET
                status = ?,
                finished_at = ?,
            total_jobs = ?,
            new_jobs = ?,
            error = ?
        WHERE id = ?
    """, (
        status,
        finished_at,
        total_jobs,
        new_jobs,
        error,
        session_id
    ))

    def fail(self, session_id: int):
        finished_at = datetime.now(UTC).isoformat()

        self.execute("""
            UPDATE crawl_sessions
            SET status = ?, finished_at = ?
            WHERE id = ?
        """, ("failed", finished_at, session_id))

    def get_by_id(self, session_id: int) -> Optional[CrawlSession]:
        row = self.fetch_one("""
            SELECT * FROM crawl_sessions WHERE id = ?
        """, (session_id,))

        if not row:
            return None

        return CrawlSession(
            id=row["id"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            status=row["status"],
            keyword=row["keyword"],
            account=row["account"],
            total_jobs=row["total_jobs"],
            new_jobs=row["new_jobs"],
            error=row["error"],
        )

    def count(self) -> int:
        row = self.fetch_one("SELECT COUNT(*) as count FROM crawl_sessions")
        return row["count"]
    
    def get_recent(self, limit: int = 10):
        rows = self.fetch_all("""
            SELECT * FROM crawl_sessions
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        return [
            CrawlSession(
                id=row["id"],
                started_at=row["started_at"],
                finished_at=row["finished_at"],
                status=row["status"],
                keyword=row["keyword"],
                account=row["account"],
                total_jobs=row["total_jobs"],
                new_jobs=row["new_jobs"],
                error=row["error"],
            )
            for row in rows
        ]

