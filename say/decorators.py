import functools

from flask import jsonify, make_response

from say.orm import obj_to_dict


def json(func, *args, **kwargs):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, tuple):
            return make_response(*result)

        return jsonify(obj_to_dict(result))

    return wrapper
