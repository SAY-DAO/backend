import os
from urllib.parse import urlparse

from humps import camel


SECRET_PATH = '/run/secrets/'


def to_camel(string):
    return camel.case(string)


def strip_scheme(url):
    parsed = urlparse(url)
    scheme = "%s://" % parsed.scheme
    return parsed.geturl().replace(scheme, '', 1)


def get_secret(secret_name, default=None):
    try:
        secret_file_path = os.path.join(SECRET_PATH, secret_name)
        with open(secret_file_path, 'r') as secret_file:
            return secret_file.read().strip()
    except IOError:
        env_name = secret_name.upper().replace('-', '_')
        return os.environ.get(env_name, default)
