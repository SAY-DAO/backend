import functools
from logging import getLogger

import redis
from flask import jsonify
from flask import make_response
from flask.globals import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_claims
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import verify_jwt_refresh_token_in_request
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_jwt_extended.utils import create_refresh_token
from jwt.exceptions import PyJWTError
from sentry_sdk import set_user

from say.api.ext import jwt
from say.config import configs
from say.constants import BEARER
from say.constants import REFRESH_TOKEN_SW_PREFIX
from say.constants import REFRESH_TOKEN_USER_PREFIX
from say.exceptions import HTTP_PERMISION_DENIED
from say.exceptions import HTTP_UNAUTHORIZED
from say.models import SocialWorker
from say.models import User
from say.orm import session
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


def get_refresh_identity(prefix):
    raw_id = get_jwt_identity()
    if raw_id is None or not raw_id.startswith(prefix):
        return None

    return raw_id.replace(prefix, '')


def create_user_access_token(user, fresh=False):
    return BEARER + create_access_token(
        identity=user.id,
        fresh=fresh,
        user_claims=dict(
            username=user.userName,
            firstName=user.firstName,
            lastName=user.lastName,
            avatarUrl=user.avatarUrl,
        ),
    )


def create_user_refresh_token(user):
    id = REFRESH_TOKEN_USER_PREFIX + str(user.id)
    return BEARER + create_refresh_token(identity=id)


def user_identity_refresh_token():
    return get_refresh_identity(REFRESH_TOKEN_USER_PREFIX)


def sw_identity_refresh_token():
    return get_refresh_identity(REFRESH_TOKEN_SW_PREFIX)


def create_sw_access_token(social_worker, fresh=False):
    return BEARER + create_access_token(
        identity=social_worker.id,
        fresh=fresh,
        user_claims=dict(
            username=social_worker.username,
            firstName=social_worker.first_name,
            lastName=social_worker.last_name,
            avatarUrl=social_worker.avatar_url,
            role=social_worker.privilege.name,
            ngoId=social_worker.ngo_id,
        ),
    )


def create_sw_refresh_token(social_worker):
    id = REFRESH_TOKEN_SW_PREFIX + str(social_worker.id)
    return BEARER + create_refresh_token(identity=id)


def verify_refresh_token(prefix):
    try:
        verify_jwt_refresh_token_in_request()
        id = get_jwt_identity()
        if id is None:
            raise HTTP_UNAUTHORIZED()

        if not id.startswith(prefix):
            raise HTTP_UNAUTHORIZED()

    except (PyJWTError, JWTExtendedException):
        raise HTTP_UNAUTHORIZED()


def authorize_refresh(func):
    def wrapper(*args, **kwargs):
        verify_refresh_token(REFRESH_TOKEN_USER_PREFIX)
        return func(*args, **kwargs)

    return wrapper


def authorize_refresh_sw(func):
    def wrapper(*args, **kwargs):
        verify_refresh_token(REFRESH_TOKEN_SW_PREFIX)
        return func(*args, **kwargs)

    return wrapper


def authorize(*roles):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt_claims()
                user_id = get_jwt_identity()
                user_role = claims.get('role', USER)

                set_user(
                    dict(
                        id=user_id,
                        role=user_role,
                    )
                )

                if user_role not in roles:
                    raise HTTP_PERMISION_DENIED()

                user = None
                if user_role == USER:
                    user = (
                        session.query(User)
                        .filter(User.id == user_id, User.isDeleted.is_(False))
                        .one_or_none()
                    )
                    if user is None:
                        raise HTTP_UNAUTHORIZED()

                else:
                    user = (
                        session.query(SocialWorker)
                        .filter(
                            SocialWorker.id == user_id,
                            SocialWorker.is_deleted.is_(False),
                            SocialWorker.is_active.is_(True),
                        )
                        .one_or_none()
                    )
                    if user is None:
                        raise HTTP_UNAUTHORIZED()

                request.user = user

            except (PyJWTError, JWTExtendedException) as ex:
                getLogger().info(ex)
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
    get_revoked_store().set(
        jti,
        'true',
        expire,
    )
