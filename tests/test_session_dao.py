from datetime import UTC, datetime

from julca_bakalarka.db.dao.session_dao import SessionDAO


async def test_start_session_new() -> None:
    dao = SessionDAO()
    now = datetime.now(UTC)
    await dao.start_session("p1", now, school_code="SC01", class_number=3)

    sessions = await dao.get_all_sessions()
    assert len(sessions) == 1
    assert sessions[0]["participant_id"] == "p1"
    assert sessions[0]["school_code"] == "SC01"
    assert sessions[0]["class_number"] == 3


async def test_start_session_existing() -> None:
    dao = SessionDAO()
    t1 = datetime(2026, 1, 1, tzinfo=UTC)
    t2 = datetime(2026, 1, 2, tzinfo=UTC)

    await dao.start_session("p1", t1, school_code="OLD")
    await dao.start_session("p1", t2, school_code="NEW")

    sessions = await dao.get_all_sessions()
    assert len(sessions) == 1
    assert sessions[0]["school_code"] == "NEW"


async def test_complete_session() -> None:
    dao = SessionDAO()
    start = datetime(2026, 1, 1, tzinfo=UTC)
    end = datetime(2026, 1, 1, 0, 5, tzinfo=UTC)

    await dao.start_session("p1", start)
    await dao.complete_session("p1", end, duration_ms=300000)

    sessions = await dao.get_all_sessions()
    assert sessions[0]["duration_ms"] == 300000
    assert sessions[0]["completed_at"] is not None


async def test_delete_session() -> None:
    dao = SessionDAO()
    await dao.start_session("p1", datetime.now(UTC))
    await dao.delete_session("p1")

    sessions = await dao.get_all_sessions()
    assert len(sessions) == 0


async def test_get_all_sessions() -> None:
    dao = SessionDAO()
    now = datetime.now(UTC)
    await dao.start_session("p1", now)
    await dao.start_session("p2", now)

    sessions = await dao.get_all_sessions()
    assert len(sessions) == 2
