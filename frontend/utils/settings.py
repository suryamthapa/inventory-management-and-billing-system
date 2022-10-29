import frontend.config as Settings
from backend.api.settings import get_setting, get_settings


def getSettings():
    status, settings = get_settings()
    if status:
        return settings
    else:
        return {}

def refreshCurrentSettings():
    status, settings = get_settings()
    if status:
        Settings.CURRENT_SETTINGS = settings