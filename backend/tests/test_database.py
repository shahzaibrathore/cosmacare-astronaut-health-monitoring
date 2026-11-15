"""Database WAL, persistence and concurrency tests."""
import threading

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal, engine
from app.models import CrewMember, TelemetryRecord


def test_wal_mode_enabled():
    with engine.connect() as conn:
        mode = conn.execute(text("PRAGMA journal_mode;")).scalar()

    assert mode.lower() == "wal"


def test_tables_created():
    with engine.connect() as conn:
        tables = [
            row[0]
            for row in conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table';")
            ).fetchall()
        ]

    for table in ("crew_members", "telemetry_records", "alert_logs"):
        assert table in tables


@pytest.mark.parametrize("crew_count", [1, 5, 10, 50])
def test_insert_crew(db_session, crew_count):
    for i in range(crew_count):
        db_session.add(
            CrewMember(name=f"Crew-{i}-{crew_count}", role="Astronaut")
        )

    db_session.commit()
    assert db_session.query(CrewMember).count() == crew_count


def test_unique_name_constraint(db_session):
    db_session.add(CrewMember(name="UniqueTest", role="X"))
    db_session.commit()

    db_session.add(CrewMember(name="UniqueTest", role="Y"))

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_transactional_rollback(db_session):
    db_session.add(CrewMember(name="RollbackTest", role="X"))
    db_session.commit()

    count_before = db_session.query(CrewMember).count()

    try:
        db_session.add(CrewMember(name="RollbackTest", role="Y"))
        db_session.commit()
    except Exception:
        db_session.rollback()

    assert db_session.query(CrewMember).count() == count_before


@pytest.mark.parametrize("n", [10, 25, 100])
def test_bulk_telemetry_insert(db_session, n):
    db_session.add(CrewMember(id=1, name="BulkCrew", role="X"))
    db_session.commit()

    for i in range(n):
        db_session.add(
            TelemetryRecord(
                crew_id=1,
                heart_rate=70 + i % 10,
                spo2=98.0,
                body_temp=37.0,
                systolic_bp=120,
                diastolic_bp=80,
            )
        )

    db_session.commit()
    assert db_session.query(TelemetryRecord).count() == n


def test_concurrent_writes():
    db1 = SessionLocal()
    db2 = SessionLocal()

    try:
        db1.add(CrewMember(id=100, name="Concurrent-A", role="X"))
        db2.add(CrewMember(id=101, name="Concurrent-B", role="X"))

        db1.commit()
        db2.commit()

        assert db1.query(CrewMember).filter(CrewMember.id == 100).count() == 1
        assert db2.query(CrewMember).filter(CrewMember.id == 101).count() == 1
    finally:
        db1.close()
        db2.close()


@pytest.mark.parametrize("batch_size", [1, 5, 20])
def test_multi_thread_ingestion(batch_size):
    errors = []

    def worker(thread_id):
        db = SessionLocal()
        try:
            for i in range(batch_size):
                db.add(
                    CrewMember(
                        id=1000 + thread_id * 100 + i,
                        name=f"T{thread_id}-Crew-{i}",
                        role="X",
                    )
                )

            db.commit()
        except Exception as exc:
            db.rollback()
            errors.append(str(exc))
        finally:
            db.close()

    threads = [
        threading.Thread(target=worker, args=(i,))
        for i in range(3)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert errors == [], f"Concurrent writes failed: {errors}"


def test_session_isolation():
    db1 = SessionLocal()
    db2 = SessionLocal()

    try:
        db1.add(CrewMember(name="IsolationTest", role="X"))
        db1.commit()

        assert (
            db2.query(CrewMember)
            .filter(CrewMember.name == "IsolationTest")
            .count()
            == 1
        )
    finally:
        db1.close()
        db2.close()


@pytest.mark.parametrize(
    "param,val",
    [
        ("heart_rate", 75),
        ("heart_rate", 120),
        ("spo2", 98.5),
        ("spo2", 95.0),
        ("body_temp", 37.0),
        ("body_temp", 36.5),
        ("systolic_bp", 120),
        ("systolic_bp", 140),
        ("diastolic_bp", 80),
        ("diastolic_bp", 90),
    ],
)
def test_persist_single_field(db_session, param, val):
    db_session.add(
        CrewMember(id=500, name=f"PersistTest-{param}-{val}", role="X")
    )
    db_session.commit()

    record = TelemetryRecord(
        crew_id=500,
        heart_rate=75,
        spo2=98.0,
        body_temp=37.0,
        systolic_bp=120,
        diastolic_bp=80,
    )

    setattr(record, param, val)
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)

    assert getattr(record, param) == val