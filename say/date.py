from datetime import datetime, timedelta
from khayyam import JalaliDate


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def format_jalali_date(date):
    return f'{date.weekdayname()} ' \
        f'{int(date.strftime("%d"))} ' \
        f'{date.monthname()} ' \
        f'ماه'


def parse_datetime(datetime_string):
    return datetime.strptime(
        datetime_string,
        DATETIME_FORMAT,
    )

