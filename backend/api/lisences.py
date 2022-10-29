import datetime
import logging
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import IntegrityError
from backend.database.deps import get_db
from backend.models.lisences import Lisences
from backend.utils.lisences import verify_lisence_key


log = logging.getLogger("backend")

def get_lisence(db: Session = get_db()):
    lisence = db.query(Lisences).order_by(Lisences.id.desc()).first()
    if not lisence: 
        db.close()
        return False, f"Lisence not found."

    payload = {
        "lisence_key":lisence.lisence_key,
        "activated_on":lisence.activated_on,
        "status": lisence.status,
        "duration":lisence.duration
    }
    db.close()
    return True, payload


def add_lisence(data:dict ={}, db: Session=get_db()):
    if not verify_lisence_key(data.get("lisence_key")):
        return False, "Invalid Lisence Key."

    lisence = Lisences(lisence_key=data.get("lisence_key"), 
                    activated_on=datetime.datetime.now(),
                    duration=data.get("duration"))
    try:
        db.add(lisence)
        db.commit()
        db.refresh(lisence)
        db.close()
        return lisence.lisence_key, "Lisence key registered successfully!"
    except IntegrityError:
        db.close()
        return False, "Lisence key already used."
    except Exception as e:
        db.close()
        return False, "Error occured. Please contact the developer."


def update_lisence(key: str, data: dict = {}, db: Session=get_db()):
    if not key: return False, "Please provide valid key."
    if key==data.get("lisence_key"): return False, "Please provide different lisence key."

    lisence = db.query(Lisences).order_by(Lisences.lisence_key == key).first()
    if not lisence: 
        db.close()
        return False, "Lisence with given key does not exist."
    
    for key, value in data.items():
        setattr(lisence, key, value)
    
    try:
        db.commit()
        db.close()
        return True, "Lisence updated successfully!"
    except Exception as e:
        db.close()
        return False, "Error occured. Please contact the developer."


def delete_lisence(id=None, db: Session=get_db()):
    if not id: return False, "Please provide valid id."

    try:
        db.query(Lisences).filter(Lisences.id==id).delete()
        db.commit()
        db.close()
        return id, "Customer deleted successfully!"
    except Exception as e:
        db.close()
        return False, "Error occured. Please contact the developer."