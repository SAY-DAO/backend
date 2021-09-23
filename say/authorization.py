import functools
from logging import getLogger

import redis
from flask import jsonify
from flask import make_response
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_claims
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import verify_jwt_refresh_token_in_request
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import PyJWTError
from sentry_sdk import set_user

from say.api.ext import jwt
from say.config import configs
from say.roles import *


_revoked_store = None


def get_revoked_store():
    global _revoked_store
    if not _revoked_store:
        _revoked_store = redis.StrictRedis(
            host=configs.REDIS_HOST,
            port=configs.REDIS_PORT,
            db=configs.REVOKED_TOKEN_STORE_DB,
            decode_responses=True,
        )

    return _revoked_store


def get_user_role():
    verify_jwt_in_request()
    return get_jwt_claims().get('role', USER)


@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token['jti']
    entry = get_revoked_store().get(jti)
    return True if entry else False


def create_user_access_token(user, fresh=False):
    return create_access_token(
        identity=user.id,
        fresh=fresh,
        user_claims=dict(
            username=user.userName,
            firstName=user.firstName,
            lastName=user.lastName,
            avatarUrl=user.avatarUrl,
        ),
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
        ),
    )


def authorize_refresh(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_refresh_token_in_request()
        except (PyJWTError, JWTExtendedException) as ex:
            return make_response(jsonify(message='Unauthorized'), 401)

        return func(*args, **kwargs)

    return wrapper


def authorize(*roles):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                set_user(
                    dict(
                        id=get_jwt_identity(),
                        role=get_user_role(),
                    )
                )
            except (PyJWTError, JWTExtendedException) as ex:
                getLogger().info(ex)
                return make_response(jsonify(message=f'Unauthorized, {ex}'), 401)

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
    get_revoked_store().set(
        jti,
        'true',
        expire,
    )
