from say.locale import get_locale

from say.exceptions import InvalidLocale

from .fa import ContentFA
from .en import ContentEN


class Content:

    def __getitem__(self, key):
        locale = get_locale()

        if locale == 'fa':
            return getattr(ContentFA, key)

        elif locale == 'en':
            return getattr(ContentEN, key)

        raise InvalidLocale(f'Invalid locale: {locale}')

content = Content()
