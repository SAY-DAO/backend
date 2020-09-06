import i18n

from .locale import get_locale


def setup():
    # Cache in memrory
    i18n.set('enable_memoization', True)

    # Skip root en or fa key in yml
    i18n.set('skip_locale_root_data', True)

    # To remove {namespace} from filename format
    # https://github.com/danhper/python-i18n#file-namespaces
    i18n.set('filename_format', '{locale}.{format}')

    i18n.load_path.append('./content')


def t(*args, locale=None, **kwargs):
    locale = locale or get_locale()

    return i18n.t(*args, locale=locale, **kwargs)


setup()
