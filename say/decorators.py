import functools
import types
from inspect import isclass

import pydantic
import ujson
from flask import Response
from flask import jsonify
from flask import make_response
from flask import request
from pydantic import ValidationError
from sqlalchemy.orm.query import Query

from say.exceptions import HTTP_NOT_FOUND
from say.orm import obj_to_dict
from say.orm import session
from say.schema.base import AllOptionalMeta


def json(schema, use_list=False):
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
                if schema:
                    if use_list:
                        return Response(
                            # Using dumb loads/dumps workaround becuase pydantic doesn't
                            # direct list serialization
                            # See https://github.com/samuelcolvin/pydantic/issues/1409
                            ujson.dumps(
                                [
                                    ujson.loads(schema.from_orm(row).json(by_alias=True))
                                    for row in result
                                ]
                            ),
                            mimetype='application/json',
                        )
                    else:
                        row = result.one_or_none()
                        if row is None:
                            raise HTTP_NOT_FOUND()

                        return Response(
                            schema.from_orm(row).json(by_alias=True),
                            mimetype='application/json',
                        )

                return jsonify([obj_to_dict(item) for item in result])

            elif isinstance(result, types.GeneratorType):
                return jsonify([obj_to_dict(item) for item in result])

            elif isclass(schema) and issubclass(schema, pydantic.BaseModel):
                if not use_list:
                    result = schema.from_orm(result).json(by_alias=True)
                else:
                    # Using dumb loads/dumps workaround becuase pydantic doesn't
                    # direct list serialization
                    # See https://github.com/samuelcolvin/pydantic/issues/1409
                    result = ujson.dumps(
                        [
                            ujson.loads(schema.from_orm(row).json(by_alias=True))
                            for row in result
                        ]
                    )
                return Response(
                    result,
                    mimetype='application/json',
                )

            elif isinstance(result, pydantic.BaseModel):
                return Response(result.json(by_alias=True), mimetype='application/json')

            return jsonify(obj_to_dict(result))

        return wrapper

    if schema and not (isclass(schema) and issubclass(schema, pydantic.BaseModel)):
        f = schema
        schema = None
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


def query(model, *filters, enbale_filtering=False, filtering_schema=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _query = session.query(model)

            # Apply custom filters
            if len(args) != 0:
                _query = _query.filter(*filters)

            # Apply query string filtering
            if enbale_filtering:
                assert (
                    filtering_schema is not None
                ), 'filteing_schema is required when enbale_filtering is True'

                class FilteringSchema(filtering_schema, metaclass=AllOptionalMeta):
                    class Config:
                        extra = 'ignore'

                data = FilteringSchema.parse_obj(request.args)
                _query = _query.filter_by(**data.dict(exclude_unset=True))

            request._query = _query
            return func(*args, **kwargs)

        return wrapper

    return decorator
