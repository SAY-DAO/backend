from flask import request, g

from .langs import LANGS


class ChangeLocaleTo:
    def __init__(self, locale):
        self.locale = locale

    def __enter__(self):
        self.prev_locale = get_locale()
        set_locale(self.locale)

    def __exit__(self, exception_type, exception_value, traceback):
        set_locale(self.prev_locale)


DEFAULT_LOCALE = LANGS.fa


def set_locale(locale):
    locale = str(locale)
    g.locale = locale.lower()


def get_locale():
    if hasattr(g, 'locale'):
        return g.locale

    try:
        return request.args['_lang'].lower()
    except:
        return DEFAULT_LOCALE
