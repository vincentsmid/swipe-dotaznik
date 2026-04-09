from julca_bakalarka.db.dao.question_dao import QuestionDAO
from julca_bakalarka.db.dao.response_dao import ResponseDAO


async def _create_question(order: int = 1) -> int:
    dao = QuestionDAO()
    q = await dao.create(text=f"Q{order}", media_filename=f"q{order}.gif", order=order)
    return q.id  # type: ignore[attr-defined]


async def test_create_response() -> None:
    qid = await _create_question()
    dao = ResponseDAO()
    await dao.create(
        participant_id="p1", question_id=qid, answer="yes", duration_ms=500
    )
    responses = await dao.get_by_participant("p1")
    assert len(responses) == 1
    assert responses[0]["answer"] == "yes"
    assert responses[0]["duration_ms"] == 500


async def test_get_by_participant() -> None:
    qid = await _create_question()
    dao = ResponseDAO()
    await dao.create(participant_id="p1", question_id=qid, answer="yes")
    await dao.create(participant_id="p2", question_id=qid, answer="no")

    p1 = await dao.get_by_participant("p1")
    assert len(p1) == 1
    assert p1[0]["participant_id"] == "p1"


async def test_get_all() -> None:
    qid = await _create_question()
    dao = ResponseDAO()
    await dao.create(participant_id="p1", question_id=qid, answer="yes")
    await dao.create(participant_id="p2", question_id=qid, answer="no")

    all_resp = await dao.get_all()
    assert len(all_resp) == 2


async def test_get_all_participant_ids() -> None:
    qid = await _create_question()
    dao = ResponseDAO()
    await dao.create(participant_id="bob", question_id=qid, answer="yes")
    await dao.create(participant_id="alice", question_id=qid, answer="no")

    ids = await dao.get_all_participant_ids()
    assert sorted(ids) == ["alice", "bob"]


async def test_delete_by_participant() -> None:
    qid = await _create_question()
    dao = ResponseDAO()
    await dao.create(participant_id="p1", question_id=qid, answer="yes")
    await dao.create(participant_id="p2", question_id=qid, answer="no")

    await dao.delete_by_participant("p1")
    remaining = await dao.get_all()
    assert len(remaining) == 1
    assert remaining[0]["participant_id"] == "p2"


async def test_get_answered_question_ids() -> None:
    q1 = await _create_question(1)
    q2 = await _create_question(2)
    dao = ResponseDAO()
    await dao.create(participant_id="p1", question_id=q1, answer="yes")
    await dao.create(participant_id="p1", question_id=q2, answer="no")

    answered = await dao.get_answered_question_ids("p1")
    assert sorted(answered) == sorted([q1, q2])
