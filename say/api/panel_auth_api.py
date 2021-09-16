from datetime import datetime

import argon2
from flasgger import swag_from
from flask import request
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_raw_jwt
from flask_restful import Resource

from say.api.ext import api
from say.authorization import authorize
from say.authorization import authorize_refresh
from say.authorization import create_sw_access_token
from say.authorization import revoke_jwt
from say.config import configs
from say.decorators import json
from say.models.social_worker_model import SocialWorker
from say.orm import safe_commit
from say.orm import session
from say.roles import *


'''
Panel Authentication APIs
'''


class PanelLogin(Resource):

    @json
    @swag_from('./docs/panel_auth/login.yml')
    def post(self):
        if 'username' in request.form.keys():
            username = request.form['username']
        else:
            return {'message': 'username is needed!!!'}, 400

        if 'password' in request.form.keys():
            password = request.form['password']
        else:
            return {'message': 'password is needed!!!'}, 400

        social_worker = session.query(SocialWorker) \
            .filter_by(isDeleted=False) \
            .filter_by(isActive=True) \
            .filter_by(userName=username) \
            .one_or_none()

        if social_worker is None:
            return {'message': 'Please Register First'}, 303

        try:
            social_worker.validate_password(password)
        except argon2.exceptions.VerifyMismatchError:
            return {'message': 'UserName or Password is Wrong'}, 303

        social_worker.lastLogin = datetime.utcnow()
        safe_commit(session)

        access_token = create_sw_access_token(social_worker)

        refresh_token = create_refresh_token(
            identity=social_worker.id,
        )

        return {
            'message': 'Login Successful',
            'access_token': f'Bearer {access_token}',
            'refresh_token': f'Bearer {refresh_token}',
        }


class PanelTokenRefresh(Resource):

    @authorize_refresh
    @json
    @swag_from('./docs/panel_auth/refresh.yml')
    def post(self):
        id = get_jwt_identity()
        social_worker = session.query(SocialWorker).get(id)
        access_token = create_sw_access_token(social_worker, fresh=True)
        refresh_token = create_refresh_token(identity=social_worker.id)

        jti = get_raw_jwt()['jti']
        revoke_jwt(jti, int(configs.JWT_REFRESH_TOKEN_EXPIRES * 1.1))

        return {
            'access_token': f'Bearer {access_token}',
            'refresh_token': f'Bearer {refresh_token}',
        }


class PanelLogoutAccess(Resource):
    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/panel_auth/logout-access.yml')
    def post(self):
        jti = get_raw_jwt()['jti']
        revoke_jwt(jti, int(configs.JWT_ACCESS_TOKEN_EXPIRES * 1.1))
        return {}, 200


class PanelLogoutRefresh(Resource):
    @authorize_refresh
    @swag_from('./docs/panel_auth/logout-refresh.yml')
    def post(self):
        jti = get_raw_jwt()['jti']
        revoke_jwt(jti, int(configs.JWT_REFRESH_TOKEN_EXPIRES * 1.1))
        return {}, 200


api.add_resource(PanelLogin, '/api/v2/panel/auth/login')
api.add_resource(PanelTokenRefresh, '/api/v2/panel/auth/refresh')
api.add_resource(PanelLogoutAccess, '/api/v2/panel/auth/logout/token')
api.add_resource(PanelLogoutRefresh, '/api/v2/panel/auth/logout/refresh')
#api.add_resource(Logout, '/api/v2/panel/auth/logout/userid=<user_id>')
#api.add_resource(Verify, '/api/v2/panel/auth/verify/userid=<user_id>')
#api.add_resource(VerifyResend, '/api/v2/panel/auth/verify/resend/userid=<user_id>')
