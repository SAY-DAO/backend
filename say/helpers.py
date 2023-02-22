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


def paginate_query(query, request, pagination_schema):
    take, skip = get_skip_take(request, pagination_schema)
    count = query.count()
    result = query.limit(take).offset(skip)
    return result, count


def paginate_list(list, request, pagination_schema):
    take, skip = get_skip_take(request, pagination_schema)
    count = len(list)
    result = list[skip + 1 : skip + 1 + take]
    return result, count


def get_skip_take(request, pagination_schema):
    pagination = pagination_schema.parse_obj(request.headers)
    take = pagination.take
    skip = pagination.skip
    return take, skip
