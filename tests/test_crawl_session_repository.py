import os
import pytest

from src.db.database_manager import DatabaseManager


@pytest.fixture
def db():
    db_path = "test_database.db"

    manager = DatabaseManager(db_path)
    manager.initialize()

    yield manager

    manager.close()   # 👈 BẮT BUỘC
    os.remove(db_path)



# ==========================
# TEST CRAWL SESSION REPO
# ==========================

def test_start_session(db):
    session_id = db.crawl_session_repo.start(
        keyword="python",
        account="acc1"
    )

    assert session_id is not None
    assert db.crawl_session_repo.count() == 1

    session = db.crawl_session_repo.get_by_id(session_id)

    assert session is not None
    assert session.status == "running"
    assert session.keyword == "python"
    assert session.account == "acc1"
    assert session.total_jobs == 0
    assert session.new_jobs == 0


def test_finish_session_success(db):
    session_id = db.crawl_session_repo.start()

    db.crawl_session_repo.finish(
        session_id=session_id,
        total_jobs=20,
        new_jobs=5,
        status="success"
    )

    session = db.crawl_session_repo.get_by_id(session_id)

    assert session.status == "success"
    assert session.total_jobs == 20
    assert session.new_jobs == 5
    assert session.finished_at is not None


def test_finish_session_failed(db):
    session_id = db.crawl_session_repo.start()

    db.crawl_session_repo.finish(
        session_id=session_id,
        total_jobs=10,
        new_jobs=2,
        status="failed",
        error="Timeout error"
    )

    session = db.crawl_session_repo.get_by_id(session_id)

    assert session.status == "failed"
    assert session.error == "Timeout error"


def test_get_recent_sessions(db):
    db.crawl_session_repo.start(keyword="k1")
    db.crawl_session_repo.start(keyword="k2")
    db.crawl_session_repo.start(keyword="k3")

    sessions = db.crawl_session_repo.get_recent(limit=2)

    assert len(sessions) == 2
    assert sessions[0].keyword == "k3"
    assert sessions[1].keyword == "k2"


def test_count_sessions(db):
    assert db.crawl_session_repo.count() == 0

    db.crawl_session_repo.start()
    db.crawl_session_repo.start()

    assert db.crawl_session_repo.count() == 2
