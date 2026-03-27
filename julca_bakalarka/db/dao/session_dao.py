from datetime import datetime
from typing import Any

from julca_bakalarka.db.models.session_model import SurveySession


class SessionDAO:
    """Data access object for the SurveySession table."""

    async def start_session(
        self,
        participant_id: str,
        started_at: datetime,
    ) -> None:
        """Record when participant starts the real survey."""
        existing = await SurveySession.select().where(
            SurveySession.participant_id == participant_id
        )
        if existing:
            await SurveySession.update({SurveySession.started_at: started_at}).where(
                SurveySession.participant_id == participant_id
            )
        else:
            await SurveySession.insert(
                SurveySession(
                    participant_id=participant_id,
                    started_at=started_at,
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

    async def get_all_sessions(self) -> list[dict[str, Any]]:
        """Get all sessions."""
        return await SurveySession.select()
