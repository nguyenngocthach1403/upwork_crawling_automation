from .connection import Database
from .repositories.job_repository import JobRepository
from .repositories.seen_job_repository import SeenJobRepository
from .repositories.crawl_session_repository import CrawlSessionRepository


class DatabaseManager:
    def __init__(self, db_path: str):
        self.database = Database(db_path)

        self.job_repo = JobRepository(self.database)
        self.seen_repo = SeenJobRepository(self.database)
        self.crawl_session_repo = CrawlSessionRepository(self.database)

    def initialize(self):
        self.job_repo.initialize()
        self.seen_repo.initialize()
        self.crawl_session_repo.initialize()

    def close(self):
        self.database.close() 
