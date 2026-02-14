from dataclasses import dataclass
from typing import Optional


@dataclass
class CrawlSession:
    id: Optional[int]
    started_at: str
    finished_at: Optional[str]
    status: str
    keyword: Optional[str]
    account: Optional[str]
    total_jobs: int
    new_jobs: int
    error: Optional[str]

    @staticmethod
    def from_db_row(row: dict) -> "CrawlSession":
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
