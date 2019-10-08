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


class CheckUser(Resource):
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            if "username" in request.json.keys():
                username = request.json["username"]
            else:
                return Response(
                    json.dumps({"message": "username is needed !!!"}), status=500
                )

            alreadyTaken = (
                session.query(UserModel)
                .filter_by(isDeleted=False)
                .filter_by(userName=username)
                .first()
            )
            if alreadyTaken is not None:
                resp = Response(
                    json.dumps(
                        {"status": False, "Message": "UserName is Already Taken"}
                    ),
                    status=200,
                )
            else:
                resp = Response(
                    json.dumps({"status": True, "Message": "UserName is Acceptable"}),
                    status=200,
                )

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "ERROR OCCURRED"}))

        finally:
            session.close()
            return resp


class PanelLogin(Resource):

    @swag_from("./docs/panel_auth/login.yml")
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "Something is Wrong!"}

        try:

            if "username" in request.json.keys():
                username = request.json["username"]
            else:
                return Response(
                    json.dumps({"message": "username is needed !!!"}), status=500
                )

            if "password" in request.json.keys():
                password = md5(request.json["password"].encode()).hexdigest()
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


#class Logout(Resource):
#
#    @jwt_required
#    def post(self, user_id):
#        session_maker = sessionmaker(db)
#        session = session_maker()
#        resp = {"message": "fuck"}
#
#        try:
#            user = session.query(UserModel).filter_by(id=user_id).first()
#            user.token = ""
#            session.commit()
#            resp = Response(
#                json.dumps({"message": "user is successfully logged out."}), status=200
#            )
#
#        except Exception as e:
#            print(e)
#            resp = Response(json.dumps({"message": "Something is Wrong!"}), status=500)
#
#        finally:
#            session.close()
#            return resp
#
#
#
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

#
#
#class Verify(Resource):
#    decorators = [limiter.limit("5/minute")]
#
#    @swag_from("./docs/auth/verify.yml")
#    def post(self, user_id):
#        session_maker = sessionmaker(db)
#        session = session_maker()
#        resp = {"message": "Something is Wrong"}
#
#        try:
#            user = session.query(UserModel).filter_by(id=user_id).first()
#            if user.isVerified:
#                resp = Response(
#                    json.dumps({"message": "User is already verified."}), status=200
#                )
#                return
#
#            verify = session.query(VerifyModel).filter_by(id_user=user_id).first()
#            from pudb import set_trace; set_trace()
#            if (
#                verify is None
#                or "verifyCode" not in request.json.keys()
#                or verify.expire_at < datetime.utcnow()
#                or verify.code != request.json["verifyCode"]
#            ):
#                resp = Response(
#                    json.dumps({"message": "Something is Wrong!"}), status=500
#                )
#                return
#
#            user.isVerified = True
#            session.commit()
#            resp = Response(
#                json.dumps({"message": "User successfully verified."}), status=200
#            )
#
#        except Exception as e:
#            print(e)
#            resp = Response(json.dumps({"message": "Something is Wrong!"}), status=500)
#
#        finally:
#            session.close()
#            return resp
#
#
#class VerifyResend(Resource):
#    decorators = [limiter.limit("2/minute")]
#
#    @swag_from("./docs/auth/verify-resend.yml")
#    def post(self, user_id):
#        session_maker = sessionmaker(db)
#        session = session_maker()
#        resp = {"message": "Something is Wrong"}
#
#        try:
#            user = session.query(UserModel).filter_by(id=user_id).first()
#            if user.isVerified:
#                resp = Response(
#                    json.dumps({"message": "User is already verified."}), status=200
#                )
#                return
#
#            verify = session.query(VerifyModel).filter_by(id_user=user_id).first()
#            if verify is None:
#                verify = VerifyModel(user=user)
#                session.add(verify)
#            verify.code = randint(100000, 999999)
#            verify.expireAt = datetime.utcnow() + timedelta(minutes=5)
#
#            session.commit()
#            send_verify_email(user.emailAddress, verify.code)
#            resp = Response(json.dumps({"message": "Verify Email Sent."}), status=200)
#
#        except Exception as e:
#            print(e)
#            resp = Response(json.dumps({"message": "Something is Wrong!"}), status=500)
#
#        finally:
#            session.close()
#            return resp
#

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
