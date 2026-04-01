import csv
import io
import uuid
from pathlib import Path
from typing import Any

import aiofiles  # type: ignore[import-untyped]
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from julca_bakalarka.db.dao.question_dao import QuestionDAO
from julca_bakalarka.db.dao.response_dao import ResponseDAO
from julca_bakalarka.db.dao.session_dao import SessionDAO
from julca_bakalarka.settings import settings
from julca_bakalarka.web.api.admin.schema import (
    QuestionResponse,
    SurveyResponseItem,
)

router = APIRouter()

ALLOWED_EXTENSIONS = {".gif", ".mp4", ".webm", ".webp", ".jpg", ".jpeg", ".png"}


@router.get("/questions", response_model=list[QuestionResponse])
async def list_questions() -> list[dict[str, Any]]:
    """List all questions."""
    dao = QuestionDAO()
    return await dao.get_all_ordered()


@router.post("/questions", response_model=QuestionResponse)
async def create_question(
    text: str = Form(...),
    order: int = Form(0),
    is_practice: bool = Form(False),
    media: UploadFile = File(...),
) -> dict[str, Any]:
    """Create a new question with media upload."""
    ext = Path(media.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Nepodporovaný typ souboru. Povolené: "
            f"{', '.join(ALLOWED_EXTENSIONS)}",
        )

    filename = f"{uuid.uuid4().hex}_{media.filename}"
    filepath = settings.media_dir / filename

    async with aiofiles.open(filepath, "wb") as f:
        content = await media.read()
        await f.write(content)

    dao = QuestionDAO()
    if order == 0:
        order = await dao.get_max_order() + 1

    question = await dao.create(
        text=text,
        media_filename=filename,
        order=order,
        is_practice=is_practice,
    )
    return {
        "id": question.id,  # type: ignore[attr-defined]
        "text": text,
        "media_filename": filename,
        "order": order,
        "is_practice": is_practice,
    }


@router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    text: str = Form(...),
    order: int = Form(...),
    is_practice: bool = Form(False),
    media: UploadFile | None = File(None),
) -> dict[str, Any]:
    """Update a question. Media file is optional."""
    dao = QuestionDAO()
    existing = await dao.get_by_id(question_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Otázka nenalezena")

    update_data: dict[str, Any] = {
        "text": text,
        "order": order,
        "is_practice": is_practice,
    }

    if media and media.filename:
        ext = Path(media.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Nepodporovaný typ souboru. Povolené: "
                f"{', '.join(ALLOWED_EXTENSIONS)}",
            )

        # Remove old file
        old_path = settings.media_dir / existing["media_filename"]
        old_path.unlink(missing_ok=True)

        filename = f"{uuid.uuid4().hex}_{media.filename}"
        filepath = settings.media_dir / filename
        async with aiofiles.open(filepath, "wb") as f:
            content = await media.read()
            await f.write(content)
        update_data["media_filename"] = filename
    else:
        update_data["media_filename"] = existing["media_filename"]

    await dao.update(question_id, **update_data)
    return {"id": question_id, **update_data}


@router.delete("/questions/{question_id}")
async def delete_question(question_id: int) -> dict[str, Any]:
    """Delete a question and its media file."""
    dao = QuestionDAO()
    existing = await dao.get_by_id(question_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Otázka nenalezena")

    # Remove media file
    media_path = settings.media_dir / existing["media_filename"]
    media_path.unlink(missing_ok=True)

    await dao.delete(question_id)
    return {"ok": True}


@router.get("/responses", response_model=list[SurveyResponseItem])
async def list_responses() -> list[dict[str, Any]]:
    """List all survey responses."""
    dao = ResponseDAO()
    return await dao.get_all()


@router.get("/sessions")
async def list_sessions() -> list[dict[str, Any]]:
    """List all survey sessions."""
    dao = SessionDAO()
    return await dao.get_all_sessions()


@router.delete("/participants/{participant_id}")
async def delete_participant(participant_id: str) -> dict[str, Any]:
    """Delete all responses and session for a participant."""
    response_dao = ResponseDAO()
    session_dao = SessionDAO()
    await response_dao.delete_by_participant(participant_id)
    await session_dao.delete_session(participant_id)
    return {"ok": True}


@router.get("/export/csv")
async def export_csv() -> StreamingResponse:
    """Export all responses as a CSV file."""
    question_dao = QuestionDAO()
    response_dao = ResponseDAO()

    questions = await question_dao.get_survey_questions()
    participant_ids = await response_dao.get_all_participant_ids()
    all_responses = await response_dao.get_all()

    # Build lookups: (participant_id, question_id) -> answer / duration
    answer_lookup = {}
    duration_lookup = {}
    for resp in all_responses:
        key = (resp["participant_id"], resp["question"])
        answer_lookup[key] = resp["answer"]
        if resp.get("duration_ms") is not None:
            duration_lookup[key] = round(resp["duration_ms"] / 1000, 1)

    # Build session lookup for total durations
    session_dao = SessionDAO()
    all_sessions = await session_dao.get_all_sessions()
    session_lookup = {s["participant_id"]: s for s in all_sessions}

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    # Header: Participant | School Code | Class
    # | Q1 answer | Q1 time | ... | Count | Duration
    header = ["Účastník", "Kód školy", "Třída"]
    for q in questions:
        header.append(q["text"])
        header.append(f"{q['text']} (s)")
    header += ["Počet odpovědí", "Čas vyplnění (s)"]
    writer.writerow(header)

    # One row per participant
    for pid in participant_ids:
        answers = [answer_lookup.get((pid, q["id"]), "N/A") for q in questions]
        answered_count = sum(1 for a in answers if a and a != "N/A")

        session = session_lookup.get(pid)
        duration_seconds = ""
        school_code = ""
        class_number = ""
        if session:
            if session.get("duration_ms") is not None:
                duration_seconds = round(session["duration_ms"] / 1000, 1)
            if session.get("school_code") is not None:
                school_code = session["school_code"]
            if session.get("class_number") is not None:
                class_number = session["class_number"]

        row: list[Any] = [pid, school_code, class_number]
        for q in questions:
            key = (pid, q["id"])
            row.append(answer_lookup.get(key, "N/A"))
            row.append(duration_lookup.get(key, ""))
        row += [answered_count, duration_seconds]
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=vysledky_dotazniku.csv",
        },
    )
