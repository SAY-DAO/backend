from datetime import datetime, timedelta
from khayyam import JalaliDate


def format_jalali_date(date):
    return f'{date.weekdayname()} ' \
        f'{int(date.strftime("%d"))} ' \
        f'{date.monthname()} ' \
        f'ماه'

