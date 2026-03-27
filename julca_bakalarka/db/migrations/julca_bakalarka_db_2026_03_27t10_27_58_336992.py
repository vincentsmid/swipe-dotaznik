from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import BigInt
from piccolo.columns.indexes import IndexMethod

ID = "2026-03-27T10:27:58:336992"
VERSION = "1.33.0"
DESCRIPTION = ""


async def forwards() -> MigrationManager:
    manager = MigrationManager(
        migration_id=ID, app_name="julca_bakalarka_db", description=DESCRIPTION
    )

    manager.add_column(
        table_class_name="SurveyResponse",
        tablename="survey_response",
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

    return manager
