from piccolo.conf.apps import AppRegistry
from piccolo.engine.sqlite import SQLiteEngine

from julca_bakalarka.settings import settings

DB = SQLiteEngine(path=str(settings.db_file))


APP_REGISTRY = AppRegistry(apps=["julca_bakalarka.db.app_conf"])
