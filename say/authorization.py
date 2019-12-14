
import functools
from flask import jsonify, request, make_response
from flask_jwt_extended import verify_jwt_in_request, get_jwt_claims, \
    get_jwt_identity

from say.roles import *


def authorize(*roles):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except:
                return make_response(jsonify(message='Unauthorized'), 401)

            claims = get_jwt_claims()

            jwt_role = claims.get('role', USER)
            if jwt_role not in roles:
                return make_response(jsonify(message='Permission Denied'), 403)

            return func(*args, **kwargs)

        return wrapper

    if roles and callable(roles[0]):
        f = roles[0]
        roles = [USER]  # Default role, can be override
        return decorator(f)
    else:
        return decorator


def get_user_id():
    return get_jwt_identity()

