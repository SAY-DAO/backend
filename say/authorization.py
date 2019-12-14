
import functools
from flask import jsonify, request, make_response
from flask_jwt_extended import verify_jwt_in_request, get_jwt_claims, \
    get_jwt_identity


def authorize(*roles):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except:
                return make_response(jsonify(message='Unauthorized'), 401)

            claims = get_jwt_claims()

            if len(roles) != 0 and claims.get('roles', None) not in roles:
                return make_response(jsonify(message='Permission Denied'), 403)

            return func(*args, **kwargs)

        return wrapper

    if roles and callable(roles[0]):
        f = roles[0]
        roles = []
        return decorator(f)
    else:
        return decorator


def get_user_id():
    return get_jwt_identity()

