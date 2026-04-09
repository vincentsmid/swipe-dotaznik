from typing import Any

from julca_bakalarka.db.dao.question_dao import QuestionDAO


async def test_create_question() -> None:
    dao = QuestionDAO()
    q = await dao.create(text="Is this a test?", media_filename="img.gif", order=5)
    assert q.text == "Is this a test?"  # type: ignore[attr-defined]
    assert q.media_filename == "img.gif"  # type: ignore[attr-defined]
    assert q.order == 5  # type: ignore[attr-defined]
    assert q.is_practice is False  # type: ignore[attr-defined]


async def test_create_practice_question() -> None:
    dao = QuestionDAO()
    q = await dao.create(
        text="Practice?", media_filename="p.gif", order=1, is_practice=True
    )
    assert q.is_practice is True  # type: ignore[attr-defined]


async def test_get_all_ordered() -> None:
    dao = QuestionDAO()
    await dao.create(text="Real 2", media_filename="r2.gif", order=2)
    await dao.create(text="Real 1", media_filename="r1.gif", order=1)
    await dao.create(text="Practice", media_filename="p.gif", order=1, is_practice=True)

    questions = await dao.get_all_ordered()
    assert len(questions) == 3
    # Practice questions come first
    assert questions[0]["is_practice"] is True
    # Then real questions sorted by order
    assert questions[1]["text"] == "Real 1"
    assert questions[2]["text"] == "Real 2"


async def test_get_by_id(sample_question: dict[str, Any]) -> None:
    dao = QuestionDAO()
    result = await dao.get_by_id(sample_question["id"])
    assert result is not None
    assert result["text"] == "Test question?"


async def test_get_by_id_not_found() -> None:
    dao = QuestionDAO()
    result = await dao.get_by_id(99999)
    assert result is None


async def test_update_question(sample_question: dict[str, Any]) -> None:
    dao = QuestionDAO()
    await dao.update(sample_question["id"], text="Updated?", order=10)
    result = await dao.get_by_id(sample_question["id"])
    assert result is not None
    assert result["text"] == "Updated?"
    assert result["order"] == 10


async def test_delete_question(sample_question: dict[str, Any]) -> None:
    dao = QuestionDAO()
    await dao.delete(sample_question["id"])
    result = await dao.get_by_id(sample_question["id"])
    assert result is None


async def test_get_practice_questions() -> None:
    dao = QuestionDAO()
    await dao.create(text="Real", media_filename="r.gif", order=1)
    await dao.create(text="Practice", media_filename="p.gif", order=1, is_practice=True)

    practice = await dao.get_practice_questions()
    assert len(practice) == 1
    assert practice[0]["text"] == "Practice"


async def test_get_survey_questions() -> None:
    dao = QuestionDAO()
    await dao.create(text="Real", media_filename="r.gif", order=1)
    await dao.create(text="Practice", media_filename="p.gif", order=1, is_practice=True)

    survey = await dao.get_survey_questions()
    assert len(survey) == 1
    assert survey[0]["text"] == "Real"


async def test_get_max_order_empty() -> None:
    dao = QuestionDAO()
    assert await dao.get_max_order() == 0


async def test_get_max_order_with_data() -> None:
    dao = QuestionDAO()
    await dao.create(text="Q1", media_filename="q1.gif", order=3)
    await dao.create(text="Q2", media_filename="q2.gif", order=7)
    assert await dao.get_max_order() == 7
