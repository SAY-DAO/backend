import functools
import types

from flask import Response
from flask import jsonify
from flask import make_response
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
    
        elif isinstance(result, types.GeneratorType):
            return jsonify([
                obj_to_dict(item)
                for item in result
            ])
        
        return jsonify(obj_to_dict(result))

    return wrapper
