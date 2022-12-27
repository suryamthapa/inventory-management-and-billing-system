from pytz import timezone
import pytz
from core import nepali_datetime

def get_nepali_datetime_from_utc(utc_datetime, format="bs"):
    try:
        nepali_timezone = timezone("Asia/Kathmandu")
        utc = pytz.utc
        utc_datetime = utc_datetime.replace(tzinfo=utc)
        ne_datetime_ad = utc_datetime.astimezone(nepali_timezone)
        if format.lower()=="ad":
            return ne_datetime_ad, ""
        elif format.lower()=="bs":
            ne_datetime_bs = nepali_datetime.datetime.from_datetime_datetime(ne_datetime_ad)
            return ne_datetime_bs, ""
        else:
            return None, "Invalid format"
    except Exception as e:
        return None, e