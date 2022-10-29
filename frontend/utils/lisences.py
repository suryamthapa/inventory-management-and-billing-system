import datetime
import logging
import frontend.config as Settings
from backend.api.lisences import get_lisence, update_lisence
from backend.models import LisenceStatus


log = logging.getLogger("frontend")


def refreshLisenceInfo():
    info = getLisenceInfo()
    Settings.LISENCE_INFO = info

def getLisenceInfo():
    status, message = get_lisence()
    payload = {
        "status": getLisenceStatus(status, message),
        "activated_on": message["activated_on"] if status else None,
        "lisence_key": message["lisence_key"] if status else None,
        "duration": message["duration"] if status else None,
    }
    return payload


def getLisenceStatus(status, message):
    if status:
        if message["status"] == LisenceStatus.expired:
            return LisenceStatus.expired

        current_time = datetime.datetime.now()
        activated_on = message["activated_on"]
        duration  = message["duration"] if message["duration"] else 1
        # check if expired, if yes update db
        if (activated_on - current_time).seconds > duration*365*86400:
            data = {"status": LisenceStatus.expired}
            status, message = update_lisence(message["lisence_key"], data)
            if status:
                return LisenceStatus.expired
            else:
                log.error(message)
                return None
        
        return LisenceStatus.active
    
    return LisenceStatus.not_activated_yet