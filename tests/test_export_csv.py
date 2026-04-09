import csv
import io
from datetime import UTC, datetime
from typing import Any

from httpx import AsyncClient
from starlette import status

from julca_bakalarka.db.dao.response_dao import ResponseDAO
from julca_bakalarka.db.dao.session_dao import SessionDAO


async def test_export_csv_empty(
    client: AsyncClient,
    admin_auth: tuple[str, str],
) -> None:
    response = await client.get("/api/admin/export/csv", auth=admin_auth)
    assert response.status_code == status.HTTP_200_OK
    assert "text/csv" in response.headers["content-type"]

    reader = csv.reader(io.StringIO(response.text), delimiter=";")
    rows = list(reader)
    # Should have header row only
    assert len(rows) == 1
    assert rows[0][0] == "Účastník"


async def test_export_csv_with_data(
    client: AsyncClient,
    admin_auth: tuple[str, str],
    sample_question: dict[str, Any],
) -> None:
    # Create session and response
    session_dao = SessionDAO()
    response_dao = ResponseDAO()

    await session_dao.start_session(
        "p1",
        datetime(2026, 1, 1, tzinfo=UTC),
        school_code="SC01",
        class_number=5,
    )
    await session_dao.complete_session(
        "p1",
        datetime(2026, 1, 1, 0, 5, tzinfo=UTC),
        duration_ms=300000,
    )
    await response_dao.create(
        participant_id="p1",
        question_id=sample_question["id"],
        answer="yes",
        duration_ms=2000,
    )

    response = await client.get("/api/admin/export/csv", auth=admin_auth)
    assert response.status_code == status.HTTP_200_OK

    reader = csv.reader(io.StringIO(response.text), delimiter=";")
    rows = list(reader)
    assert len(rows) == 2  # header + 1 participant

    header = rows[0]
    data_row = rows[1]

    # Check header structure
    assert header[0] == "Účastník"
    assert header[1] == "Kód školy"
    assert header[2] == "Třída"

    # Check data
    assert data_row[0] == "p1"
    assert data_row[1] == "SC01"
    assert data_row[2] == "5"
    # Answer column
    assert data_row[3] == "yes"
    # Duration column (seconds)
    assert data_row[4] == "2.0"
    # Answer count
    assert data_row[-2] == "1"
    # Total duration (seconds)
    assert data_row[-1] == "300.0"
