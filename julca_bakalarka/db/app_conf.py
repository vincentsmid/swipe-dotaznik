from pathlib import Path

from piccolo.conf.apps import AppConfig, table_finder

CURRENT_DIRECTORY = Path(__file__).parent


APP_CONFIG = AppConfig(
    app_name="julca_bakalarka_db",
    migrations_folder_path=str(CURRENT_DIRECTORY / "migrations"),
    table_classes=table_finder(
        modules=[
            "julca_bakalarka.db.models.dummy_model",
            "julca_bakalarka.db.models.question_model",
            "julca_bakalarka.db.models.response_model",
            "julca_bakalarka.db.models.session_model",
        ],
    ),
    migration_dependencies=[],
    commands=[],
)
