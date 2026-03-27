from datetime import datetime

from pydantic import BaseModel


class QuestionResponse(BaseModel):
    """Response model for a question."""

    id: int
    text: str
    media_filename: str
    order: int
    is_practice: bool


class SurveyResponseItem(BaseModel):
    """Response model for a single survey response."""

    id: int
    participant_id: str
    question: int
    answer: str
    answered_at: datetime | None = None
