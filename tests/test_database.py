import os
import pytest

from src.db.database_manager import DatabaseManager
from src.models.job_model import Job


@pytest.fixture
def db():
    db_path = "test_database.db"

    manager = DatabaseManager(db_path)
    manager.initialize()

    yield manager

    manager.close()      # 👈 BẮT BUỘC
    os.remove(db_path)



def create_sample_job():
    return Job(
        job_id="job123",
        title="Python Developer",
        posted_text="1 hour ago",
        posted_minutes_ago=60,
        location="Remote",
        description="Test job",
        job_type="Hourly",
        budget={"min": 10, "max": 20},
        experience_level="Intermediate",
        skills=["Python", "SQL"],
        activities={"proposals": 5},
        client={"rating": 4.9},
        url="https://upwork.com/job123"
    )


# ==========================
# TEST JOB REPO
# ==========================

def test_insert_and_get_job(db):
    job = create_sample_job()

    db.job_repo.upsert(job)

    fetched = db.job_repo.get_by_job_id("job123")

    assert fetched is not None
    assert fetched.title == "Python Developer"
    assert fetched.budget["min"] == 10


def test_update_job(db):
    job = create_sample_job()
    db.job_repo.upsert(job)

    job.title = "Updated Title"
    db.job_repo.upsert(job)

    fetched = db.job_repo.get_by_job_id("job123")
    assert fetched.title == "Updated Title"


def test_count_jobs(db):
    db.job_repo.upsert(create_sample_job())
    assert db.job_repo.count() == 1


def test_delete_job(db):
    db.job_repo.upsert(create_sample_job())
    db.job_repo.delete("job123")

    assert db.job_repo.get_by_job_id("job123") is None


# ==========================
# TEST SEEN REPO
# ==========================

def test_mark_seen(db):
    db.seen_repo.mark_seen("job123")

    assert db.seen_repo.is_seen("job123") is True
    assert db.seen_repo.count() == 1


def test_filter_unseen(db):
    db.seen_repo.mark_seen("job1")

    result = db.seen_repo.filter_unseen(["job1", "job2", "job3"])

    assert result == ["job2", "job3"]
