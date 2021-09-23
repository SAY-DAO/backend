import functools
import types
from typing import Type
from typing import TypeVar

from flask import Response
from flask import jsonify
from flask import make_response
from flask import request
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
            return jsonify([obj_to_dict(item) for item in result])

        elif isinstance(result, types.GeneratorType):
            return jsonify([obj_to_dict(item) for item in result])

        return jsonify(obj_to_dict(result))

    return wrapper


def validate(schema):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                data = schema(
                    **(request.args or {}),
                    **(request.json or {}),
                    **(request.form or {}),
                    **(request.files or {}),
                )
            except ValueError as e:
                return e.json(), 400

            return func(*args, **kwargs, data=data)

        return wrapper

    return decorator
