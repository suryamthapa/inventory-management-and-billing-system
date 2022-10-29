from backend.api.about_app import add_update_app_configuration, get_about_app
import datetime
import logging


log = logging.getLogger("frontend")


def is_trial_complete(forceComplete=False):
    if forceComplete:
        data = {"trial_completed": True}
        status, message = add_update_app_configuration(data)
        if status:
            return True
        else:
            log.error(message)
            return False
    else:
        status, message = get_about_app()
        if status:
            if message["trial_completed"]:
                return True
            if not message["trial_begin_on"]:
                return False
                
            current_time = datetime.datetime.now()
            trial_begin_on = message["trial_begin_on"]
            
            if (trial_begin_on - current_time).seconds > 7*86400:
                data = {"trial_completed": True}
                status, message = add_update_app_configuration(data)
                if status:
                    return True
                else:
                    log.error(message)
                    return False
            return False
        
        return False


def has_trial_started():
    status, message = get_about_app()
    if status:
        if message["trial_begin_on"]:
            return True, message["trial_begin_on"]
        return False, ""
    else:
        return False, ""


def start_trial():
    data = {
        "trial_begin_on": datetime.datetime.now()
    }
    status, message = add_update_app_configuration(data)
    if status:
        return True, "STARTED: trial for 7 days"
    else:
        return False, message