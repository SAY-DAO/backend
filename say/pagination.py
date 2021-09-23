import functools

from flask import jsonify
from flask import make_response
from flask import request


def paginate(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            skip = int(request.args.get('skip', 0))
            take = min(int(request.args.get('take', 10)), 100)

            request.skip = skip
            request.take = take

        except ValueError as ex:
            return make_response(jsonify(message='Invaid skip or take'), 400)

        return func(*args, **kwargs)

    return wrapper
