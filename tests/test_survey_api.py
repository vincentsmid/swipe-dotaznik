from typing import Any

from httpx import AsyncClient
from starlette import status

from julca_bakalarka.db.dao.response_dao import ResponseDAO


async def test_start_survey(
    client: AsyncClient,
    sample_question: dict[str, Any],
    sample_practice_question: dict[str, Any],
) -> None:
    response = await client.post(
        "/api/survey/start",
        json={"participant_id": "p1"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    # Practice questions should come first
    assert data[0]["is_practice"] is True
    assert data[1]["is_practice"] is False


async def test_start_survey_empty_id(client: AsyncClient) -> None:
    response = await client.post(
        "/api/survey/start",
        json={"participant_id": "  "},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_get_questions(
    client: AsyncClient,
    sample_question: dict[str, Any],
) -> None:
    response = await client.get("/api/survey/questions")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == sample_question["id"]


async def test_submit_answer_valid(
    client: AsyncClient,
    sample_question: dict[str, Any],
) -> None:
    for answer in ["yes", "no", "skip", "N/A"]:
        response = await client.post(
            "/api/survey/answer",
            json={
                "participant_id": f"p_{answer}",
                "question_id": sample_question["id"],
                "answer": answer,
                "duration_ms": 1000,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"ok": True}


async def test_submit_answer_invalid(
    client: AsyncClient,
    sample_question: dict[str, Any],
) -> None:
    response = await client.post(
        "/api/survey/answer",
        json={
            "participant_id": "p1",
            "question_id": sample_question["id"],
            "answer": "maybe",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_submit_answer_empty_id(
    client: AsyncClient,
    sample_question: dict[str, Any],
) -> None:
    response = await client.post(
        "/api/survey/answer",
        json={
            "participant_id": " ",
            "question_id": sample_question["id"],
            "answer": "yes",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_get_progress(
    client: AsyncClient,
    sample_question: dict[str, Any],
) -> None:
    # Submit an answer first
    dao = ResponseDAO()
    await dao.create(
        participant_id="p1",
        question_id=sample_question["id"],
        answer="yes",
    )

    response = await client.get("/api/survey/progress/p1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert sample_question["id"] in data["answered_question_ids"]


async def test_start_session(client: AsyncClient) -> None:
    response = await client.post(
        "/api/survey/session/start",
        json={
            "participant_id": "p1",
            "started_at": "2026-01-01T00:00:00Z",
            "school_code": "SC01",
            "class_number": 3,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"ok": True}


async def test_start_session_empty_id(client: AsyncClient) -> None:
    response = await client.post(
        "/api/survey/session/start",
        json={
            "participant_id": " ",
            "started_at": "2026-01-01T00:00:00Z",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_complete_session(
    client: AsyncClient,
    sample_question: dict[str, Any],
) -> None:
    # Start session first
    await client.post(
        "/api/survey/session/start",
        json={
            "participant_id": "p1",
            "started_at": "2026-01-01T00:00:00Z",
        },
    )

    # Complete session - should fill N/A for unanswered questions
    response = await client.post(
        "/api/survey/session/complete",
        json={
            "participant_id": "p1",
            "completed_at": "2026-01-01T00:05:00Z",
            "duration_ms": 300000,
        },
    )
    assert response.status_code == status.HTTP_200_OK

    # Verify N/A was filled for the unanswered question
    dao = ResponseDAO()
    responses = await dao.get_by_participant("p1")
    assert len(responses) == 1
    assert responses[0]["answer"] == "N/A"


async def test_complete_session_empty_id(client: AsyncClient) -> None:
    response = await client.post(
        "/api/survey/session/complete",
        json={
            "participant_id": " ",
            "completed_at": "2026-01-01T00:05:00Z",
            "duration_ms": 300000,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
