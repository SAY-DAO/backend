from datetime import datetime, timedelta
from hashlib import md5
from random import randint
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    jwt_refresh_token_required, get_jwt_identity, get_raw_jwt
)
from . import *
from say.models.social_worker_model import SocialWorkerModel
from say.models.revoked_token_model import RevokedTokenModel


"""
Panel Authentication APIs
"""


class PanelLogin(Resource):

    @swag_from("./docs/panel_auth/login.yml")
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "Something is Wrong!"}

        try:

            if "username" in request.form.keys():
                username = request.form["username"]
            else:
                return Response(
                    json.dumps({"message": "username is needed !!!"}), status=500
                )

            if "password" in request.form.keys():
                password = md5(request.form["password"].encode()).hexdigest()
            else:
                return Response(
                    json.dumps({"message": "password is needed !!!"}), status=500
                )

            social_worker = (
                session.query(SocialWorkerModel)
                .filter_by(isDeleted=False)
                .filter_by(userName=username)
                .first()
            )
            if social_worker is not None:
                if social_worker.password == password:
                    social_worker.lastLogin = datetime.now()
                    session.commit()

                    access_token = create_access_token(
                        identity = social_worker.userName
                    )

                    refresh_token = create_refresh_token(
                        identity = social_worker.userName
                    )

                    resp = Response(
                        json.dumps(
                            {
                                "message": "Login Successful",
                                "access_token": f"Bearer {access_token}",
                                "refresh_token": f"Bearer {refresh_token}",
                            }
                        ),
                        status=200,
                    )
                else:
                    resp = Response(
                        json.dumps({"message": "UserName or Password is Wrong"}),
                        status=303,
                    )

            else:
                resp = Response(
                    json.dumps({"message": "Please Register First"}), status=303
                )

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "something is wrong"}), status=500)

        finally:
            session.close()
            return resp


class PanelTokenRefresh(Resource):

    @jwt_refresh_token_required
    @swag_from("./docs/panel_auth/refresh.yml")
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': f'Bearer {access_token}'}


class PanelLogoutAccess(Resource):
    @jwt_required
    @swag_from("./docs/panel_auth/logout-access.yml")
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        jti = get_raw_jwt()['jti']
        msg = None
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            session.add(revoked_token)
            session.commit()
            msg = {'message': 'Access token has been revoked'}
        except:
            msg = {'message': 'Something went wrong'}, 500
        finally:
            session.close()
            return msg


class PanelLogoutRefresh(Resource):
    @jwt_refresh_token_required
    @swag_from("./docs/panel_auth/logout-refresh.yml")
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            session.add(revoked_token)
            session.commit()
            msg = {'message': 'Refresh token has been revoked'}
        except:
            msg = {'message': 'Something went wrong'}, 500
        finally:
            session.close()
            return msg

"""
API URLs
"""


api.add_resource(PanelLogin, "/api/v2/panel/auth/login")
api.add_resource(PanelTokenRefresh, "/api/v2/panel/auth/refresh")
api.add_resource(PanelLogoutAccess, "/api/v2/panel/auth/logout/token")
api.add_resource(PanelLogoutRefresh, "/api/v2/panel/auth/logout/refresh")
#api.add_resource(Logout, "/api/v2/panel/auth/logout/userid=<user_id>")
#api.add_resource(Verify, "/api/v2/panel/auth/verify/userid=<user_id>")
#api.add_resource(VerifyResend, "/api/v2/panel/auth/verify/resend/userid=<user_id>")
