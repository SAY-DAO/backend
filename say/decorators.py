import functools

from flask import jsonify, make_response, Response
from sqlalchemy.orm.query import Query

from say.orm import obj_to_dict


def json(func, *args, **kwargs):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, Response):
            return result

        elif isinstance(result, tuple):
            return make_response(*result)

        elif isinstance(result, Query):
            return jsonify([
                obj_to_dict(item)
                for item in result
            ])

        return jsonify(obj_to_dict(result))

    return wrapper
