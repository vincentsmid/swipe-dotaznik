import io
from typing import Any

from httpx import AsyncClient
from starlette import status

from julca_bakalarka.db.dao.question_dao import QuestionDAO
from julca_bakalarka.db.dao.response_dao import ResponseDAO
from julca_bakalarka.db.dao.session_dao import SessionDAO
from julca_bakalarka.settings import settings


async def test_list_questions(
    client: AsyncClient,
    admin_auth: tuple[str, str],
    sample_question: dict[str, Any],
) -> None:
    response = await client.get("/api/admin/questions", auth=admin_auth)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["text"] == "Test question?"


async def test_create_question(
    client: AsyncClient,
    admin_auth: tuple[str, str],
) -> None:
    # Ensure media dir exists
    settings.media_dir.mkdir(parents=True, exist_ok=True)

    response = await client.post(
        "/api/admin/questions",
        data={"text": "New question?", "order": "1", "is_practice": "false"},
        files={"media": ("test.gif", io.BytesIO(b"fake gif data"), "image/gif")},
        auth=admin_auth,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["text"] == "New question?"
    assert data["order"] == 1
    assert data["is_practice"] is False
    assert "test.gif" in data["media_filename"]


async def test_create_question_bad_extension(
    client: AsyncClient,
    admin_auth: tuple[str, str],
) -> None:
    response = await client.post(
        "/api/admin/questions",
        data={"text": "Bad file", "order": "1"},
        files={
            "media": ("malware.exe", io.BytesIO(b"bad"), "application/octet-stream")
        },
        auth=admin_auth,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_update_question(
    client: AsyncClient,
    admin_auth: tuple[str, str],
    sample_question: dict[str, Any],
) -> None:
    response = await client.put(
        f"/api/admin/questions/{sample_question['id']}",
        data={"text": "Updated?", "order": "5", "is_practice": "false"},
        auth=admin_auth,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["text"] == "Updated?"
    assert data["order"] == 5


async def test_update_question_not_found(
    client: AsyncClient,
    admin_auth: tuple[str, str],
) -> None:
    response = await client.put(
        "/api/admin/questions/99999",
        data={"text": "Nope", "order": "1"},
        auth=admin_auth,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_question(
    client: AsyncClient,
    admin_auth: tuple[str, str],
    sample_question: dict[str, Any],
) -> None:
    # Create a media file so delete can unlink it
    media_path = settings.media_dir / sample_question["media_filename"]
    settings.media_dir.mkdir(parents=True, exist_ok=True)
    media_path.write_bytes(b"fake")

    response = await client.delete(
        f"/api/admin/questions/{sample_question['id']}",
        auth=admin_auth,
    )
    assert response.status_code == status.HTTP_200_OK

    dao = QuestionDAO()
    assert await dao.get_by_id(sample_question["id"]) is None


async def test_delete_question_not_found(
    client: AsyncClient,
    admin_auth: tuple[str, str],
) -> None:
    response = await client.delete("/api/admin/questions/99999", auth=admin_auth)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_list_responses(
    client: AsyncClient,
    admin_auth: tuple[str, str],
    sample_question: dict[str, Any],
) -> None:
    dao = ResponseDAO()
    await dao.create(
        participant_id="p1",
        question_id=sample_question["id"],
        answer="yes",
    )

    response = await client.get("/api/admin/responses", auth=admin_auth)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


async def test_list_sessions(
    client: AsyncClient,
    admin_auth: tuple[str, str],
) -> None:
    from datetime import UTC, datetime

    dao = SessionDAO()
    await dao.start_session("p1", datetime.now(UTC))

    response = await client.get("/api/admin/sessions", auth=admin_auth)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


async def test_delete_participant(
    client: AsyncClient,
    admin_auth: tuple[str, str],
    sample_question: dict[str, Any],
) -> None:
    from datetime import UTC, datetime

    response_dao = ResponseDAO()
    session_dao = SessionDAO()
    await response_dao.create(
        participant_id="p1",
        question_id=sample_question["id"],
        answer="yes",
    )
    await session_dao.start_session("p1", datetime.now(UTC))

    response = await client.delete("/api/admin/participants/p1", auth=admin_auth)
    assert response.status_code == status.HTTP_200_OK

    assert len(await response_dao.get_by_participant("p1")) == 0
    assert len(await session_dao.get_all_sessions()) == 0
