from datetime import datetime, timedelta
from hashlib import md5
from random import randint

from flask_jwt_extended import create_access_token, create_refresh_token
from flask_mail import Message

from . import *
from say.models.user_model import UserModel
from say.models.verify_model import VerifyModel


"""
Authentication APIs
"""

def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()


def send_verify_email(email, verify_code):

    verify_mail = Message(
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
            if "username" in request.form.keys():
                username = request.form["username"]
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
#            if "username" in request.form.keys():
#                username = request.form["username"]
#            else:
#                return Response(
#                    json.dumps({"message": "userName is needed !!!"}), status=500
#                )
#
#            if "password" in request.form.keys():
#                password = md5(request.form["password"].encode()).hexdigest()
#            else:
#                return Response(
#                    json.dumps({"message": "password is needed !!!"}), status=500
#                )

            if "email" in request.form.keys():
                email = request.form["email"]
            else:
                resp =  Response(json.dumps({"message": "email is needed"}), status=500)
                return

            alreadyExist = (
                session.query(UserModel)
                .filter_by(isDeleted=False)
                .filter_by(emailAddress=email)
                .first()
            )
            if alreadyExist is not None:
                resp = Response(
                    json.dumps({"status": False, "Message": "User is Already existed"}),
                    status=200,
                )
            else:
                created_at = datetime.utcnow()
                last_update = datetime.utcnow()
                last_login = datetime.utcnow()
                password = randint(100000, 999999)
                new_user = UserModel(
                    firstName="",
                    lastName="",
                    userName=email,
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

                access_token = create_access_token(
                    identity=new_user.id,
                    headers=dict(email=email),
                )

                refresh_token = create_refresh_token(
                    identity=new_user.id,
                    headers=dict(email=email),
                )

                verify = VerifyModel(user=new_user, code=password)
                session.add(verify)

                send_verify_email(new_user.emailAddress, verify.code)

                resp = make_response(
                    jsonify(
                        {
                            "message": "Register Successful",
                            "accessToken": f"Bearer {access_token}",
                            "refreshToken": f"Bearer {refresh_token}",
                            "user": obj_to_dict(new_user),
                        },
                    ),
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
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "Something is Wrong!"}

        try:

            if "username" in request.form.keys():
                username = request.form["username"]
            else:
                return Response(
                    json.dumps({"message": "userName is needed !!!"}), status=500
                )

            if "password" in request.form.keys():
                password = md5(request.form["password"].encode()).hexdigest()
            else:
                return Response(
                    json.dumps({"message": "password is needed !!!"}), status=500
                )

            user = (
                session.query(UserModel)
                .filter_by(isDeleted=False)
                .filter_by(userName=username)
                .first()
            )
            if user is not None:
                if user.password == password:
                    user.token = md5(
                        (username + user.emailAddress).encode()
                    ).hexdigest()
                    user.lastLogin = datetime.now()
                    session.commit()
                    resp = Response(
                        json.dumps(
                            {"message": "Login Successful", "userToken": user.token}
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


class Logout(Resource):
    def post(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "fuck"}

        try:
            user = session.query(UserModel).filter_by(id=user_id).first()
            user.token = ""
            session.commit()
            resp = Response(
                json.dumps({"message": "user is successfully logged out."}), status=200
            )

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "Something is Wrong!"}), status=500)

        finally:
            session.close()
            return resp


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
            if user.isVerified:
                resp = Response(
                    json.dumps({"message": "User is already verified"}), status=200
                )
                return

            verify = session.query(VerifyModel).filter_by(user_id=user_id).first()
            if (
                verify is None
                or "verifyCode" not in request.form.keys()
            ):
                resp = Response(
                    json.dumps({"message": "Something is Wrong!"}), status=400
                )
                return

            sent_verify_code = str(request.form["verifyCode"])
            sent_verify_code = sent_verify_code.replace('-', '')
            sent_verify_code = int(sent_verify_code)
            if (
                verify.expire_at < datetime.utcnow()
                or verify.code != sent_verify_code
            ):
                resp = Response(
                    json.dumps({"message": "verifyCode is Invalid!"}), status=500
                )
                return

            user.isVerified = True
            session.commit()
            resp = Response(
                json.dumps({"message": "User successfully verified."}), status=200
            )

        except Exception as e:
            print(e)
            resp = Response(
                json.dumps({"message": "Something is Wrong!", "error": str(e)}),
                status=500,
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

            user.password = verify.code
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


"""
API URLs
"""


api.add_resource(CheckUser, "/api/v2/auth/checkUserName")
api.add_resource(RegisterUser, "/api/v2/auth/register")
api.add_resource(Login, "/api/v2/auth/login")
api.add_resource(Logout, "/api/v2/auth/logout/userid=<user_id>")
api.add_resource(Verify, "/api/v2/auth/verify/userid=<user_id>")
api.add_resource(VerifyResend, "/api/v2/auth/verify/resend/userid=<user_id>")
