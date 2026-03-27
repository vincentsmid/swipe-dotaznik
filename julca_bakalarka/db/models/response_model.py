from piccolo.columns import BigInt, ForeignKey, Timestamptz, Varchar
from piccolo.table import Table

from julca_bakalarka.db.models.question_model import Question


class SurveyResponse(Table):
    """A single participant's answer to a question."""

    participant_id = Varchar(length=200)
    question = ForeignKey(references=Question)
    answer = Varchar(length=10)
    answered_at = Timestamptz(null=True, default=None)
    duration_ms = BigInt(null=True, default=None)
