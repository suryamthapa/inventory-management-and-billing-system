import os
from backend.api.about_app import add_update_app_configuration


def database_initialization():
    try:
        # ensure database, if does not exists, migrate with alembic
        if not os.path.exists("imabs.db"):
            from alembic.config import Config
            from alembic import command
            alembic_cfg = Config("./alembic.ini")
            # command.revision(config=alembic_cfg, message="Initializing database", autogenerate=True)
            command.upgrade(alembic_cfg, "head")
        return True, "INITIALIZED: database upgraded"
    except Exception as e:
        return False, f"Could not initialize database.\n\n{e}"


def initialize_app_configuration():
    try:
        data = {
            "app_version":"1.0"
        }
        status, message = add_update_app_configuration(data)
        if status:
            return True, "INITIALIZED: app configuration"
        else:
            return False, message
    except Exception as e:
        return False, f"Could not initialize app configurations.\n\n{e}"