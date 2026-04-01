import random
from typing import Any

from fastapi import APIRouter, HTTPException

from julca_bakalarka.db.dao.question_dao import QuestionDAO
from julca_bakalarka.db.dao.response_dao import ResponseDAO
from julca_bakalarka.db.dao.session_dao import SessionDAO
from julca_bakalarka.web.api.survey.schema import (
    AnswerRequest,
    QuestionOut,
    SessionCompleteRequest,
    SessionStartRequest,
    StartRequest,
)

router = APIRouter()

VALID_ANSWERS = {"yes", "no", "skip", "N/A"}


@router.post("/start", response_model=list[QuestionOut])
async def start_survey(body: StartRequest) -> list[dict[str, Any]]:
    """Validate participant ID and return the question list."""
    if not body.participant_id.strip():
        raise HTTPException(status_code=400, detail="Identifikátor nesmí být prázdný")

    dao = QuestionDAO()
    questions = await dao.get_all_ordered()

    # Split into practice (first) and real (shuffled)
    practice = [q for q in questions if q["is_practice"]]
    real = [q for q in questions if not q["is_practice"]]
    random.shuffle(real)
    ordered = practice + real

    return [
        {
            "id": q["id"],
            "text": q["text"],
            "media_url": f"/media/{q['media_filename']}",
            "is_practice": q["is_practice"],
        }
        for q in ordered
    ]


@router.get("/questions", response_model=list[QuestionOut])
async def get_questions() -> list[dict[str, Any]]:
    """Get all questions in order."""
    dao = QuestionDAO()
    questions = await dao.get_all_ordered()

    practice = [q for q in questions if q["is_practice"]]
    real = [q for q in questions if not q["is_practice"]]
    random.shuffle(real)
    ordered = practice + real

    return [
        {
            "id": q["id"],
            "text": q["text"],
            "media_url": f"/media/{q['media_filename']}",
            "is_practice": q["is_practice"],
        }
        for q in ordered
    ]


@router.post("/answer")
async def submit_answer(body: AnswerRequest) -> dict[str, Any]:
    """Submit a single answer."""
    if not body.participant_id.strip():
        raise HTTPException(status_code=400, detail="Identifikátor nesmí být prázdný")

    if body.answer not in VALID_ANSWERS:
        raise HTTPException(
            status_code=400,
            detail=f"Neplatná odpověď. Povolené: {', '.join(VALID_ANSWERS)}",
        )

    dao = ResponseDAO()
    await dao.create(
        participant_id=body.participant_id.strip(),
        question_id=body.question_id,
        answer=body.answer,
        duration_ms=body.duration_ms,
    )
    return {"ok": True}


@router.get("/progress/{participant_id}")
async def get_progress(participant_id: str) -> dict[str, Any]:
    """Get which questions a participant has already answered."""
    dao = ResponseDAO()
    answered_ids = await dao.get_answered_question_ids(participant_id)
    return {"answered_question_ids": answered_ids}


@router.post("/session/start")
async def start_session(body: SessionStartRequest) -> dict[str, Any]:
    """Record when the real survey begins."""
    pid = body.participant_id.strip()
    if not pid:
        raise HTTPException(status_code=400, detail="Identifikátor nesmí být prázdný")
    dao = SessionDAO()
    await dao.start_session(
        pid,
        body.started_at,
        school_code=body.school_code,
        class_number=body.class_number,
    )
    return {"ok": True}


@router.post("/session/complete")
async def complete_session(body: SessionCompleteRequest) -> dict[str, Any]:
    """Record survey completion, duration, and fill N/A for unanswered."""
    pid = body.participant_id.strip()
    if not pid:
        raise HTTPException(status_code=400, detail="Identifikátor nesmí být prázdný")

    # Fill N/A for unanswered questions
    question_dao = QuestionDAO()
    response_dao = ResponseDAO()

    survey_questions = await question_dao.get_survey_questions()
    answered_ids = await response_dao.get_answered_question_ids(pid)
    answered_set = set(answered_ids)

    for q in survey_questions:
        if q["id"] not in answered_set:
            await response_dao.create(
                participant_id=pid,
                question_id=q["id"],
                answer="N/A",
            )

    # Record session timing
    session_dao = SessionDAO()
    await session_dao.complete_session(pid, body.completed_at, body.duration_ms)

    return {"ok": True}
