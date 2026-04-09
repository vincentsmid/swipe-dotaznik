from piccolo.columns import BigInt, Integer, Timestamptz, Varchar
from piccolo.table import Table


class SurveySession(Table):
    """Tracks overall survey timing per participant."""

    participant_id = Varchar(length=200, unique=True)
    school_code = Varchar(length=50, null=True, default=None)
    class_number = Integer(null=True, default=None)
    started_at = Timestamptz(null=True, default=None)
    completed_at = Timestamptz(null=True, default=None)
    duration_ms = BigInt(null=True, default=None)
