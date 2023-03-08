import functools

from flask import jsonify
from flask import make_response
from flask import request

from say.schema.pagination import PaginationSchema


def paginate(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            skip = int(request.args.get('skip', 0))
            take = min(int(request.args.get('take', 10)), 100)

            request.skip = skip
            request.take = take

        except ValueError as ex:
            return make_response(jsonify(message='Invalid skip or take'), 400)

        return func(*args, **kwargs)

    return wrapper


def paginate_query(query, request, pagination_schema=PaginationSchema, max_take=None):
    _take, skip = get_skip_take(request, pagination_schema)
    count = query.count()
    if max_take:
        _take = min(max_take, _take)
    result = query.limit(_take or _take).offset(skip)
    return result, count


def paginate_list(list, request, pagination_schema=PaginationSchema):
    take, skip = get_skip_take(request, pagination_schema)
    count = len(list)
    result = list[skip + 1 : skip + 1 + take]
    return result, count


def get_skip_take(request, pagination_schema):
    pagination = pagination_schema.parse_obj(request.headers)
    take = pagination.take
    skip = pagination.skip
    return take, skip
