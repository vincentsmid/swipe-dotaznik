from datetime import datetime
from typing import Any

from julca_bakalarka.db.models.session_model import SurveySession


class SessionDAO:
    """Data access object for the SurveySession table."""

    async def start_session(
        self,
        participant_id: str,
        started_at: datetime,
        school_code: str | None = None,
        class_number: int | None = None,
    ) -> None:
        """Record when participant starts the real survey."""
        existing = await SurveySession.select().where(
            SurveySession.participant_id == participant_id
        )
        if existing:
            update_data: dict[Any, Any] = {SurveySession.started_at: started_at}
            if school_code is not None:
                update_data[SurveySession.school_code] = school_code
            if class_number is not None:
                update_data[SurveySession.class_number] = class_number
            await SurveySession.update(update_data).where(
                SurveySession.participant_id == participant_id
            )
        else:
            await SurveySession.insert(
                SurveySession(
                    participant_id=participant_id,
                    started_at=started_at,
                    school_code=school_code,
                    class_number=class_number,
                ),
            )

    async def complete_session(
        self,
        participant_id: str,
        completed_at: datetime,
        duration_ms: int,
    ) -> None:
        """Record when participant finishes the survey."""
        await SurveySession.update(
            {
                SurveySession.completed_at: completed_at,
                SurveySession.duration_ms: duration_ms,
            },
        ).where(SurveySession.participant_id == participant_id)

    async def delete_session(self, participant_id: str) -> None:
        """Delete a session by participant ID."""
        await SurveySession.delete().where(
            SurveySession.participant_id == participant_id
        )

    async def get_all_sessions(self) -> list[dict[str, Any]]:
        """Get all sessions."""
        return await SurveySession.select()
