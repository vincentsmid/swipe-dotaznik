from piccolo.apps.migrations.auto.migration_manager import MigrationManager

ID = "2026-04-09T12:00:00:000000"
VERSION = "1.33.0"
DESCRIPTION = "Change school_code from Integer to Varchar"


async def run_sql(forwards: bool = True) -> None:
    from piccolo.conf.apps import Finder

    engine = Finder().get_engine()
    if not engine:
        raise RuntimeError("No engine found")

    statements = [
        """
        CREATE TABLE survey_session_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_id VARCHAR(200) UNIQUE,
            school_code VARCHAR(50),
            class_number INTEGER,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            duration_ms BIGINT
        )
        """,
        """
        INSERT INTO survey_session_new
            (id, participant_id, school_code, class_number,
             started_at, completed_at, duration_ms)
        SELECT id, participant_id, CAST(school_code AS TEXT),
               class_number, started_at, completed_at, duration_ms
        FROM survey_session
        """,
        "DROP TABLE survey_session",
        "ALTER TABLE survey_session_new RENAME TO survey_session",
    ]
    for sql in statements:
        await engine.run_ddl(sql)


async def forwards() -> MigrationManager:
    manager = MigrationManager(
        migration_id=ID, app_name="julca_bakalarka_db", description=DESCRIPTION
    )

    manager.add_raw(run_sql)

    return manager
