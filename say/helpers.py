import os
from urllib.parse import urlparse

from humps import camel


def to_camel(string):
    return camel.case(string)


def strip_scheme(url):
    parsed = urlparse(url)
    scheme = "%s://" % parsed.scheme
    return parsed.geturl().replace(scheme, '', 1)


def get_secret(secret_name, default=None):
    try:
        with open(f'/run/secrets/{secret_name}', 'r') as secret_file:
            return secret_file.read().strip()
    except IOError:
        env_name = secret_name.upper().replace('-', '_')
        return os.environ.get(env_name, default)
