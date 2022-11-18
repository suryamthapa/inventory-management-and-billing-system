from frontend.utils.tkNepaliCalendar.config import Settings
import re
from nepali_datetime import date


def get_day_names(width='wide', context='format'):
    return Settings.nepali_days[context][width]


def get_month_names(width='wide', context='format'):
    return Settings.nepali_months[context][width]


def get_date_pattern(date_pattern):
        pattern = date_pattern.lower()
        ymd = r"^y+[^a-zA-Z]*m{1,2}[^a-z]*d{1,2}[^mdy]*$"
        mdy = r"^m{1,2}[^a-zA-Z]*d{1,2}[^a-z]*y+[^mdy]*$"
        dmy = r"^d{1,2}[^a-zA-Z]*m{1,2}[^a-z]*y+[^mdy]*$"
        res = ((re.search(ymd, pattern) is not None)
               or (re.search(mdy, pattern) is not None)
               or (re.search(dmy, pattern) is not None))
        if res:
            return pattern.replace('m', 'M')
        raise ValueError("%r is not a valid date pattern" % date_pattern)


def parse_date(string, date_pattern="MM/dd/yyyy"):
    # we try ISO-8601 format first, meaning similar to formats
    # extended YYYY-MM-DD or basic YYYYMMDD
    numbers = re.findall(r'(\d+)', string)
    iso_alike = re.match(r'^(\d{4})-?([01]\d)-?([0-3]\d)$',
                         string, flags=re.ASCII)  # allow only ASCII digits
    if iso_alike:
        try:
            return date(*map(int, iso_alike.groups()))
        except ValueError:
            pass  # a locale format might fit better, so let's continue

    format_str = date_pattern.lower()
    year_idx = format_str.index('y')
    month_idx = format_str.index('m')
    if month_idx < 0:
        month_idx = format_str.index('l')
    day_idx = format_str.index('d')

    indexes = [(year_idx, 'Y'), (month_idx, 'M'), (day_idx, 'D')]
    indexes.sort()
    indexes = {item[1]: idx for idx, item in enumerate(indexes)}

    # FIXME: this currently only supports numbers, but should also support month
    #        names, both in the requested locale, and english

    year = numbers[indexes['Y']]
    if len(year) == 2:
        year = 2000 + int(year)
    else:
        year = int(year)
    month = int(numbers[indexes['M']])
    day = int(numbers[indexes['D']])
    if month > 12:
        month, day = day, month
    return date(year, month, day)
