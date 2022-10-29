import logging
from sqlalchemy.orm import Session
from backend.database.deps import get_db
from backend.models.settings import Settings


log = logging.getLogger("backend")


def get_settings(db: Session = get_db()):
    try:
        settings = db.query(Settings).all()
        payload = {}
        for setting in settings:
            payload[setting.key] = eval(setting.value) if setting.key=="company_profile" else setting.value
        db.close()
        return True, payload
    except Exception as e:
        db.close()
        log.error(f"Error occured while fetching app settings -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def get_setting(key: str, db: Session = get_db()):
    try:
        setting = db.query(Settings).filter(Settings.key == key).first()
        if not setting:
            db.close()
            return False, f"Setting with key '{key}' does not exist."
        payload = {
            f"{key}":eval(setting.value) if key=="company_profile" else setting.value
        }
        db.close()
        return True, payload
    except Exception as e:
        db.close()
        log.error(f"Error occured while fetching app setting with key: {key} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def add_update_setting(data: dict = {}, db: Session=get_db()):
    try:
        for key, value in data.items():
            setting = db.query(Settings).filter(Settings.key==key).first()
            if setting:
                setting.value = value
                db.commit()
            else:
                setting = Settings(key=key, value=value)
                db.add(setting)
                db.commit()
        db.close()
        return True, "Updated successfully!"
    except Exception as e:
        db.close()
        log.error(f"Error occured while adding or updating app setting with data: {data} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def delete_setting(key=None, db: Session=get_db()):
    try:
        if not id: return False, "Please provide valid id."
    
        db.query(Settings).filter(Settings.key==key).delete()
        db.commit()
        db.close()
        return id, "Product deleted successfully!"
    except Exception as e:
        db.close()
        log.error(f"Error occured while deleting app setting with key: {key} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"