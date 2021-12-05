import functools
import types
from inspect import isclass

import pydantic
from flask import Response
from flask import jsonify
from flask import make_response
from flask import request
from pydantic import ValidationError
from sqlalchemy.orm.query import Query

from say.orm import obj_to_dict


def json(schema):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal schema

            result = func(*args, **kwargs)

            if isinstance(result, Response):
                return result

            elif isinstance(result, tuple):
                return make_response(*result)

            elif isinstance(result, Query):
                return jsonify([obj_to_dict(item) for item in result])

            elif isinstance(result, types.GeneratorType):
                return jsonify([obj_to_dict(item) for item in result])

            elif isclass(schema) and issubclass(schema, pydantic.BaseModel):
                return Response(
                    schema.from_orm(result).json(by_alias=True),
                    mimetype='application/json',
                )

            elif isinstance(result, pydantic.BaseModel):
                return Response(result.json(by_alias=True), mimetype='application/json')

            return jsonify(obj_to_dict(result))

        return wrapper

    if schema and not (isclass(schema) and issubclass(schema, pydantic.BaseModel)):
        f = schema
        schema = tuple()
        return decorator(f)

    return decorator


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
                    **kwargs,
                )
            except ValidationError as e:
                return e.errors(), 400

            return func(*args, **kwargs, data=data)

        return wrapper

    return decorator
