import functools
import types
from collections import OrderedDict
from inspect import isclass

import pydantic
import ujson
from flask import Response
from flask import jsonify
from flask import make_response
from flask import request
from pydantic import ValidationError
from sqlalchemy.orm.query import Query

from say.config import configs
from say.constants import OrderingDirection
from say.exceptions import HTTP_NOT_FOUND
from say.orm import obj_to_dict
from say.orm import query_builder
from say.orm import session
from say.pagination import get_skip_take, paginate_query
from say.schema.base import AllOptionalMeta
from say.schema.base import OrderingMeta
from say.schema.pagination import PaginationSchema


def json(schema, use_list=False, paginate=False):
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
                        # Using dumb loads/dumps workaround becuase pydantic doesn't
                        # direct list serialization
                        # See https://github.com/samuelcolvin/pydantic/issues/1409
                        if paginate:
                            result, count = paginate_query(
                                result, request, PaginationSchema
                            )
                            r = (
                                ujson.dumps(
                                    dict(
                                        count=count,
                                        result=[
                                            ujson.loads(
                                                schema.from_orm(row).json(by_alias=True)
                                            )
                                            for row in result
                                        ],
                                    )
                                ),
                            )
                        else:
                            r = (
                                ujson.dumps(
                                    [
                                        ujson.loads(
                                            schema.from_orm(row).json(by_alias=True)
                                        )
                                        for row in result
                                    ]
                                ),
                            )

                        return Response(
                            r,
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


def query(
    model,
    *filters,
    enable_filtering=False,
    filter_callbacks=None,
    filtering_schema=None,
    enable_pagination=False,
    enable_count=False,
    pagination_schema=PaginationSchema,
    enable_ordering=False,
    ordering_schema=None,
    ordering_desc_symbol=configs.ORDERING_DESC_SYMBOL,
    ordering_key=configs.ORDERING_KEY,
    ordering_key_separator=configs.ORDERING_KEY_SEPARATOR,
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if enable_filtering:

                class FilteringSchema(filtering_schema, metaclass=AllOptionalMeta):
                    class Config:
                        extra = 'ignore'

                filter_by = FilteringSchema.parse_obj(request.args).dict(
                    exclude_unset=True,
                )
            else:
                filter_by = None

            if enable_pagination:
                take, skip = get_skip_take(request, pagination_schema)

            else:
                take = skip = None

            if enable_ordering:

                class OrderingSchema(ordering_schema, metaclass=OrderingMeta):
                    class Config:
                        extra = 'ignore'

                string_fields = request.args.get(ordering_key, '')
                fields = string_fields.split(ordering_key_separator)
                order_by = OrderedDict()

                for f in fields:
                    if f.startswith(ordering_desc_symbol):
                        order_by[f[1:]] = OrderingDirection.Desc
                    else:
                        order_by[f] = OrderingDirection.Asc

                order_by = OrderingSchema.parse_obj(order_by).dict(exclude_unset=True)
            else:
                order_by = None

            _query, count = query_builder(
                session=session,
                model=model,
                filters=filters,
                filter_callbacks=filter_callbacks,
                filter_by=filter_by,
                skip=skip,
                take=take,
                order_by=order_by,
                enable_count=enable_count,
            )

            request._query = _query
            request.count = count
            return func(*args, **kwargs)

        return wrapper

    return decorator
