from datetime import UTC, datetime
from typing import Any

from julca_bakalarka.db.models.response_model import SurveyResponse


class ResponseDAO:
    """Data access object for the SurveyResponse table."""

    async def create(
        self,
        participant_id: str,
        question_id: int,
        answer: str,
        answered_at: datetime | None = None,
        duration_ms: int | None = None,
    ) -> None:
        """Store a single response."""
        if answered_at is None:
            answered_at = datetime.now(UTC)
        await SurveyResponse.insert(
            SurveyResponse(
                participant_id=participant_id,
                question=question_id,
                answer=answer,
                answered_at=answered_at,
                duration_ms=duration_ms,
            ),
        )

    async def get_by_participant(
        self,
        participant_id: str,
    ) -> list[dict[str, Any]]:
        """Get all responses for a participant."""
        return await SurveyResponse.select().where(
            SurveyResponse.participant_id == participant_id
        )

    async def get_all(self) -> list[dict[str, Any]]:
        """Get all responses."""
        return await SurveyResponse.select()

    async def get_all_participant_ids(self) -> list[str]:
        """Get all distinct participant IDs."""
        rows = await SurveyResponse.raw(
            "SELECT DISTINCT participant_id FROM survey_response "
            "ORDER BY participant_id",
        )
        return [row["participant_id"] for row in rows]

    async def delete_by_participant(self, participant_id: str) -> None:
        """Delete all responses for a participant."""
        await SurveyResponse.delete().where(
            SurveyResponse.participant_id == participant_id
        )

    async def get_answered_question_ids(
        self,
        participant_id: str,
    ) -> list[int]:
        """Get IDs of questions already answered by a participant."""
        rows = await SurveyResponse.select(SurveyResponse.question).where(
            SurveyResponse.participant_id == participant_id
        )
        return [row["question"] for row in rows]
