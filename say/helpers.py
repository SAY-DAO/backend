from urllib.parse import urlparse

from humps import camel


def to_camel(string):
    return camel.case(string)


def strip_scheme(url):
    parsed = urlparse(url)
    scheme = "%s://" % parsed.scheme
    return parsed.geturl().replace(scheme, '', 1)
