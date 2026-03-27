from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import BigInt
from piccolo.columns.column_types import Timestamptz
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod

ID = "2026-03-27T10:06:52:615165"
VERSION = "1.33.0"
DESCRIPTION = ""


async def forwards() -> MigrationManager:
    manager = MigrationManager(
        migration_id=ID, app_name="julca_bakalarka_db", description=DESCRIPTION
    )

    manager.add_table(
        class_name="SurveySession",
        tablename="survey_session",
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name="SurveySession",
        tablename="survey_session",
        column_name="participant_id",
        db_column_name="participant_id",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 200,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="SurveySession",
        tablename="survey_session",
        column_name="started_at",
        db_column_name="started_at",
        column_class_name="Timestamptz",
        column_class=Timestamptz,
        params={
            "default": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="SurveySession",
        tablename="survey_session",
        column_name="completed_at",
        db_column_name="completed_at",
        column_class_name="Timestamptz",
        column_class=Timestamptz,
        params={
            "default": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="SurveySession",
        tablename="survey_session",
        column_name="duration_ms",
        db_column_name="duration_ms",
        column_class_name="BigInt",
        column_class=BigInt,
        params={
            "default": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="SurveyResponse",
        tablename="survey_response",
        column_name="answered_at",
        db_column_name="answered_at",
        column_class_name="Timestamptz",
        column_class=Timestamptz,
        params={
            "default": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    return manager
