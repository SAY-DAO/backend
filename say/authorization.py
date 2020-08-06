
import functools

from flask import jsonify, make_response
from flask_jwt_extended import verify_jwt_in_request, get_jwt_claims, \
    get_jwt_identity, create_access_token, verify_jwt_refresh_token_in_request

from say.api.ext.jwt import jwt
from say.api.ext.redis import revoked_store
from say.roles import *


def get_user_role():
    return get_jwt_claims().get('role', USER)


def create_user_access_token(user, fresh=False):
    return create_access_token(
        identity=user.id,
        fresh=fresh,
        user_claims=dict(
            username=user.userName,
            firstName=user.firstName,
            lastName=user.lastName,
            avatarUrl=user.avatarUrl,
        )
    )


def create_sw_access_token(social_worker, fresh=False):
    return create_access_token(
        identity=social_worker.id,
        fresh=fresh,
        user_claims=dict(
            username=social_worker.userName,
            firstName=social_worker.firstName,
            lastName=social_worker.lastName,
            avatarUrl=social_worker.avatarUrl,
            role=social_worker.privilege.name,
            ngoId=social_worker.id_ngo,
        )
    )


def authorize_refresh(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_refresh_token_in_request()
        except:
            return make_response(jsonify(message='Unauthorized'), 401)

        return func(*args, **kwargs)

    return wrapper


def authorize(*roles):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except:
                return make_response(jsonify(message='Unauthorized'), 401)

            if get_user_role() not in roles:
                return make_response(jsonify(message='Permission Denied'), 403)

            return func(*args, **kwargs)

        return wrapper

    if roles and callable(roles[0]):
        f = roles[0]
        roles = [USER]  # Default role, can be override
        return decorator(f)
    else:
        return decorator


# Note: do not remove verify function, if u do, get_jwt_identity will return None!
def get_user_id():
    verify_jwt_in_request()
    return get_jwt_identity()


# Note: do not remove verify function, if u do, get_jwt_identity will return None!
def get_sw_ngo_id():
    verify_jwt_in_request()
    return get_jwt_claims().get('ngoId', -1)


def revoke_jwt(jti, expire):
    revoked_store.set(
        jti, 'true', expire,
    )


@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token['jti']
    entry = revoked_store.get(jti)
    return True if entry else False