from urllib.parse import urljoin
from datetime import datetime, timedelta
from random import randint

from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    jwt_refresh_token_required, get_jwt_identity, get_raw_jwt
)
from flask_mail import Message

from . import *
from say.models.user_model import UserModel
from say.models.verify_model import VerifyModel
from say.models.revoked_token_model import RevokedTokenModel

"""
Authentication APIs
"""


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


def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()


def send_verify_email(email, verify_code):

    verify_mail = Message(
        subject='SAY Email Verification',
        recipients=[email],
        html=render_template('email_verification.html', code=str(verify_code)),
    )
    mail.send(verify_mail)


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
                    json.dumps({"message": "userName is needed !!!"}), status=500
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


class RegisterUser(Resource):

    @swag_from("./docs/auth/register.yml")
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "something is wrong"}
        try:
            if "username" in request.json.keys():
                username = request.json["username"]
            else:
                resp = Response(
                    json.dumps({"message": "userName is needed !!!"}), status=500
                )
                return

            if "password" in request.json.keys():
                password = request.json["password"]
            else:
                resp = Response(
                    json.dumps({"message": "password is needed !!!"}), status=500
                )
                return

            if "email" in request.json.keys():
                email = request.json["email"]
            else:
                resp =  Response(json.dumps({"message": "email is needed"}), status=500)
                return

            if "firstName" in request.json.keys():
                first_name = request.json["firstName"]
            else:
                resp = Response(
                    json.dumps({"message": "firstName is needed !!!"}), status=500
                )
                return

            if "lastName" in request.json.keys():
                last_name = request.json["lastName"]
            else:
                resp = Response(
                    json.dumps({"message": "lastName is needed !!!"}), status=500
                )
                return

            alreadyExist = (
                session.query(UserModel)
                .filter_by(isDeleted=False)
                .filter_by(userName=username)
                .first()
            )
            if alreadyExist is not None:
                resp = Response(
                    json.dumps({"status": False, "Message": "User is Already existed"}),
                    status=500,
                )
            else:
                created_at = datetime.utcnow()
                last_update = datetime.utcnow()
                last_login = datetime.utcnow()
                new_user = UserModel(
                    firstName=first_name,
                    lastName=last_name,
                    userName=username,
                    avatarUrl=None,
                    phoneNumber=None,
                    emailAddress=email,
                    gender=None,
                    city=0,
                    country=0,
                    createdAt=created_at,
                    lastUpdate=last_update,
                    birthDate=None,
                    birthPlace=None,
                    lastLogin=last_login,
                    password=password,
                    flagUrl="",
                )
                session.add(new_user)
                session.flush()

                code = randint(100000, 999999)
                verify = VerifyModel(user=new_user, code=code)
                session.add(verify)

                send_verify_email(new_user.emailAddress, verify.code)

                resp = make_response(
                    jsonify(obj_to_dict(new_user)),
                    200,
                )
                session.commit()

        except Exception as e:
            print(e)
            resp = Response(
                json.dumps({"message": "Something is Wrong!", "error": str(e)}),
                status=500,
            )

        finally:
            session.close()
            return resp


class Login(Resource):

    @swag_from("./docs/auth/login.yml")
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "Something is Wrong!"}

        try:

            if "username" in request.form.keys():
                username = request.form["username"]
            else:
                resp = Response(
                    json.dumps({"message": "userName is needed !!!"}), status=500
                )
                return

            if "password" in request.form.keys():
                password = request.form["password"]
            else:
                resp = Response(
                    json.dumps({"message": "password is needed !!!"}), status=500
                )
                return

            user = (
                session.query(UserModel)
                .filter_by(isDeleted=False)
                .filter_by(userName=username)
                .first()
            )
            if user is not None:
                if user.validate_password(password):
                    if not user.isVerified:
                        verify = session.query(VerifyModel) \
                            .filter_by(user_id=user.id) \
                            .first()

                        if verify is None:
                            verify = VerifyModel(user=user)
                            session.add(verify)

                        verify.code = randint(100000, 999999)
                        verify.expire_at = datetime.utcnow() + timedelta(minutes=60)

                        session.commit()
                        send_verify_email(user.emailAddress, verify.code)

                        resp = make_response(
                            jsonify({
                                'user': obj_to_dict(user),
                            }),
                            302,
                        )
                        return

                    user.lastLogin = datetime.utcnow()
                    session.commit()

                    access_token = create_user_access_token(user)
                    refresh_token = create_refresh_token(identity=user.id)

                    resp = make_response(
                        jsonify(
                            {
                                "message": "Login Successful",
                                "accessToken": f"Bearer {access_token}",
                                "refreshToken": f"Bearer {refresh_token}",
                                "user": obj_to_dict(user),
                            },
                        ),
                        200,
                    )
                else:
                    resp = Response(
                        json.dumps({"message": "Username or Password is Wrong"}),
                        status=400,
                    )

            else:
                resp = Response(
                    json.dumps({"message": "Please Register First"}), status=401
                )

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "something is wrong"}), status=400)

        finally:
            session.close()
            return resp


class LogoutAccess(Resource):
    @jwt_required
    @swag_from("./docs/auth/logout-access.yml")
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        jti = get_raw_jwt()['jti']
        msg = None
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            session.add(revoked_token)
            session.commit()
            msg = {'message': 'Access token has been revoked'}
        except:
            msg = {'message': 'Something went wrong'}, 500
        finally:
            session.close()
            return msg


class LogoutRefresh(Resource):
    @jwt_refresh_token_required
    @swag_from("./docs/auth/logout-refresh.yml")
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            session.add(revoked_token)
            session.commit()
            msg = {'message': 'Refresh token has been revoked'}
        except:
            msg = {'message': 'Something went wrong'}, 500
        finally:
            session.close()
            return msg


class Verify(Resource):
    decorators = [limiter.limit("5/minute")]

    @swag_from("./docs/auth/verify.yml")
    def post(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "Something is Wrong"}

        try:
            user_id = int(user_id)
            user = session.query(UserModel).filter_by(id=user_id).first()
            verify = session.query(VerifyModel).filter_by(user_id=user_id).first()
            sent_verify_code = request.form.get('verifyCode', 'invalid')

            if not user.isVerified:
                error = None
                if (
                    verify is None
                    or str(verify.code) != sent_verify_code.replace('-', '')
                ):
                    error = 'Verify code is invalid'

                elif verify.expire_at < datetime.utcnow():
                    error = 'Verify code is expired'

                if error:
                    raise Exception(error)

            user.isVerified = True

            access_token = create_user_access_token(user)
            refresh_token = create_refresh_token(identity=user.id)

            resp = make_response(
                jsonify({
                    "message": "User successfully verified",
                    "accessToken": f"Bearer {access_token}",
                    "refreshToken": f"Bearer {refresh_token}",
                    "user": obj_to_dict(user),
                }),
                200,
            )
            session.commit()

        except Exception as e:
            print(e)
            resp = make_response(
                jsonify({"message": str(e)}),
                400,
            )

        finally:
            session.close()
            return resp


class VerifyResend(Resource):
    decorators = [limiter.limit("2/minute")]

    @swag_from("./docs/auth/verify-resend.yml")
    def post(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "Something is Wrong"}

        try:
            user = session.query(UserModel).filter_by(id=user_id).first()
            if user.isVerified:
                resp = Response(
                    json.dumps({"message": "User is already verified."}), status=200
                )
                return

            verify = session.query(VerifyModel).filter_by(user_id=user_id).first()
            if verify is None:
                verify = VerifyModel(user=user)
                session.add(verify)

            verify.code = randint(100000, 999999)
            verify.expire_at = datetime.utcnow() + timedelta(minutes=60)

            session.commit()
            send_verify_email(user.emailAddress, verify.code)
            resp = Response(json.dumps({"message": "Verify Email Sent."}), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "Something is Wrong!"}), status=500)

        finally:
            session.close()
            return resp


class TokenRefresh(Resource):

    @jwt_refresh_token_required
    @swag_from("./docs/auth/refresh.yml")
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        id = get_jwt_identity()
        user = session.query(UserModel).get(id)
        session.close()
        access_token = create_user_access_token(user, fresh=True)
        return jsonify({'accessToken': f'Bearer {access_token}'})


"""
API URLs
"""


api.add_resource(CheckUser, "/api/v2/auth/checkUserName")
api.add_resource(RegisterUser, "/api/v2/auth/register")
api.add_resource(Login, "/api/v2/auth/login")
api.add_resource(LogoutAccess, "/api/v2/auth/logout/token")
api.add_resource(LogoutRefresh, "/api/v2/auth/logout/refresh")
api.add_resource(TokenRefresh, "/api/v2/auth/refresh")
api.add_resource(Verify, "/api/v2/auth/verify/userid=<user_id>")
api.add_resource(VerifyResend, "/api/v2/auth/verify/resend/userid=<user_id>")
