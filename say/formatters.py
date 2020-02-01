from khayyam import JalaliDate

from say.langs import LANGS

int_formatter = lambda integer: format(integer, ',d')

def expose_datetime(dt, locale, with_year=True):
    if locale == LANGS.en:
        if with_year:
            return dt.strftime('%Y.%m.%d')
        else:
            return dt.strftime('%m.%d')

    elif locale == LANGS.fa:
        if with_year:
            return JalaliDate(dt).localdateformat()
        else:
            return JalaliDate(dt).strftime('%A %D %B')

    return dt



