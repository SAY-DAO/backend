from urllib.parse import urljoin

from sqlalchemy import types

from say.config import configs


class PrefixedURL(types.TypeDecorator):
    '''A type for adding a prefix to a url on way out.'''

    def __init__(self, prefix, **kwargs):
        self.prefix = prefix
        super(PrefixedURL, self).__init__(**kwargs)

    impl = types.Unicode

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return urljoin(self.prefix, value)


class ResourceURL(types.TypeDecorator):
    '''A type for adding base url to relative url on way out.'''

    def __init__(self, **kwargs):
        super(ResourceURL, self).__init__(prefix=configs.BASE_RESOURCE_URL, **kwargs)

    impl = PrefixedURL
