from datetime import datetime

from pydantic import BaseModel


class QuestionOut(BaseModel):
    """Question data returned to survey participants."""

    id: int
    text: str
    media_url: str
    is_practice: bool


class AnswerRequest(BaseModel):
    """Request body for submitting an answer."""

    participant_id: str
    question_id: int
    answer: str
    duration_ms: int | None = None


class StartRequest(BaseModel):
    """Request body for starting a survey."""

    participant_id: str


class SessionStartRequest(BaseModel):
    """Request body for starting a survey session timer."""

    participant_id: str
    started_at: datetime


class SessionCompleteRequest(BaseModel):
    """Request body for completing a survey session."""

    participant_id: str
    completed_at: datetime
    duration_ms: int
