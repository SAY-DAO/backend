import os
from datetime import datetime
from urllib.parse import urljoin

from sqlalchemy import types
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from say.config import configs
from say.utils import random_string


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


class LocalFile(types.TypeDecorator):
    '''A type for storing files on local storage and returning a url on way out.

    params:
        base_url: the base url to use for the file url
        dst: the destination folder to store the file
        keep_name: whether to keep the original filename or not
        filename_length: the length of the random filename

    '''

    def __init__(
        self,
        base_url=configs.BASE_RESOURCE_URL,
        dst=configs.UPLOAD_FOLDER,
        keep_name=False,
        filename_length=8,
        **kwargs,
    ):
        self.base_url = base_url
        self.dst = dst
        self.keep_name = keep_name
        self.filename_length = filename_length
        super(LocalFile, self).__init__(**kwargs)

    impl = types.Unicode

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        elif isinstance(value, str):
            return value

        elif isinstance(value, FileStorage):
            if self.keep_name:
                timestamp = int(datetime.utcnow().timestamp())
                name = f'{timestamp}_{secure_filename(value.filename)}'
            else:
                _, extension = os.path.splitext(value.filename)
                name = f'{random_string(self.filename_length)}{extension}'

            if not os.path.isdir(self.dst):
                os.makedirs(self.dst, exist_ok=True)

            path = os.path.join(self.dst, name)
            value.save(path)
            return path

        raise ValueError("Unsupported type for LocalFile")

    def process_result_value(self, value, dialect):
        return urljoin(self.base_url, value)
