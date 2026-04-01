from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Integer
from piccolo.columns.indexes import IndexMethod

ID = "2026-04-01T22:16:43:733294"
VERSION = "1.33.0"
DESCRIPTION = ""


async def forwards() -> MigrationManager:
    manager = MigrationManager(
        migration_id=ID, app_name="julca_bakalarka_db", description=DESCRIPTION
    )

    manager.add_column(
        table_class_name="SurveySession",
        tablename="survey_session",
        column_name="class_number",
        db_column_name="class_number",
        column_class_name="Integer",
        column_class=Integer,
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
        column_name="school_code",
        db_column_name="school_code",
        column_class_name="Integer",
        column_class=Integer,
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
