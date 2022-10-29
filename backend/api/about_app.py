import logging
from sqlalchemy.orm import Session
from backend.database.deps import get_db
from backend.models.about_app import AboutApp


log = logging.getLogger("backend")


def get_about_app(db: Session = get_db()):
    try:
        about_app = db.query(AboutApp).first()
        if not about_app: 
            db.close()
            return False, f"App info not found."

        payload = {
            "app_version":about_app.app_version,
            "trial_begin_on":about_app.trial_begin_on,
            "trial_completed": about_app.trial_completed
        }
        db.close()
        return True, payload
    except Exception as e:
        db.close()
        log.error(f"ERROR: while fetching about app configuration -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"
        



def add_update_app_configuration(data: dict = {}, db: Session=get_db()):
    try:
        if not id: return False, "Please provide valid id."
        about_app = db.query(AboutApp).first()
        if not about_app: 
            about_app = AboutApp(app_version="1.0")
            db.add(about_app)
            db.commit()
            db.close()
            return True, "App configuration initialized."
        for key, value in data.items():
            setattr(about_app, key, value)
    
        db.commit()
        db.close()
        return True, "App configuration updated successfully!"
    except Exception as e:
        db.close()
        log.error(f"ERROR: while adding or updating about app configuration -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"
    