from piccolo.columns import BigInt, Timestamptz, Varchar
from piccolo.table import Table


class SurveySession(Table):
    """Tracks overall survey timing per participant."""

    participant_id = Varchar(length=200, unique=True)
    started_at = Timestamptz(null=True, default=None)
    completed_at = Timestamptz(null=True, default=None)
    duration_ms = BigInt(null=True, default=None)
