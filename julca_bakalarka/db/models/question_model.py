from piccolo.columns import Boolean, Integer, Varchar
from piccolo.table import Table


class Question(Table):
    """Survey question with associated media."""

    text = Varchar(length=500)
    media_filename = Varchar(length=255)
    order = Integer(default=0)
    is_practice = Boolean(default=False)
