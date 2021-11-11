from urllib.parse import urljoin

from sqlalchemy import types

from say.config import configs


class PrefixString(types.TypeDecorator):
    '''A type for adding a prefix to a string on way out.'''

    def __init__(self, prefix, **kwargs):
        self.prefix = prefix
        super(PrefixString, self).__init__(**kwargs)

    impl = types.Unicode

    def process_result_value(self, value, dialect):
        return urljoin(self.prefix, value)


class ResourceURL(types.TypeDecorator):
    '''A type for adding base url to relative url.'''

    def __init__(self, **kwargs):
        super(ResourceURL, self).__init__(prefix=configs.BASE_URL, **kwargs)

    impl = PrefixString
