"""Pytest fixtures with isolated in-memory DB per test session."""
import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Isolate DB BEFORE importing app modules
_tmpdir = tempfile.mkdtemp(prefix="cosmacare-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_tmpdir) / 'test.db'}"
os.environ["ENABLE_AUTO_SEED"] = "true"

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

TEST_DB_PATH = Path(_tmpdir) / "test.db"

test_engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}",
    connect_args={"check_same_thread": False, "timeout": 15},
    future=True,
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


@pytest.fixture(scope="function", autouse=True)
def _fresh_schema():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture()
def db_session():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    def _override_get_db():
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def valid_payload():
    return {
        "crew_id": 1,
        "heart_rate": 75,
        "spo2": 98.0,
        "body_temp": 37.0,
        "systolic_bp": 120,
        "diastolic_bp": 80,
    }