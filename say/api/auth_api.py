from datetime import datetime, timedelta
from random import randint

from babel import Locale
from flask_jwt_extended import create_refresh_token, \
    jwt_refresh_token_required, get_jwt_identity, get_raw_jwt
from sqlalchemy_utils import PhoneNumber


from . import *
from say.models import session, obj_to_dict, or_, commit,  ResetPassword, \
    Verification, User, RevokedToken, and_
from say.render_template_i18n import render_template_i18n
from say.tasks import send_embeded_subject_email, send_sms
from say.locale import ChangeLocaleTo
from say.content import content


"""
Authentication APIs
"""

def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()


def send_verify_sms(to_user, verify_code):
    with ChangeLocaleTo(to_user.locale):
        send_sms.delay(
            to_user.phone_number.e164,
            content['CONFIRM_PHONE'] % verify_code,
        )


def send_verify_email(to_user, verify_code):
    send_embeded_subject_email.delay(
        to=to_user.emailAddress,
        html=render_template_i18n(
            'email_verification.html',
            code=str(verify_code),
            locale=get_locale(),
        ),
    )


class CheckUser(Resource):
    def post(self):
        resp = {"message": "major error occurred!"}

        try:
            if "username" in request.json.keys():
                username = request.json["username"]
            else:
                return Response(
                    json.dumps({"message": "userName is needed !!!"}), status=500
                )

            alreadyTaken = (
                session.query(User)
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
        resp = {"message": "something is wrong"}, 500
        try:
            if "username" in request.json.keys():
                username = request.json["username"].lower()
            else:
                resp = Response(
                    json.dumps({"message": "userName is needed !!!"}), status=500
                )
                return

            if "phoneNumber" in request.json.keys():
                phoneNumber = request.json["phoneNumber"].lstrip('0')
            else:
                resp = Response(
                    json.dumps({"message": "phoneNumber is needed !!!"}), status=500
                )
                return

            if "country_code" in request.json.keys():
                country_code = request.json["country_code"]
            else:
                resp = Response(
                    json.dumps({"message": "country_code is needed !!!"}), status=500
                )
                return

            if "password" in request.json.keys():
                password = request.json["password"]
            else:
                resp = Response(
                    json.dumps({"message": "password is needed !!!"}), status=500
                )
                return

            email = None
            if "email" in request.json.keys():
                email = request.json["email"].lower()

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

            lang = get_locale()
            locale = Locale(lang)
            phone_number = PhoneNumber(phoneNumber, country_code)

            alreadyExist = (
                session.query(User)
                .filter_by(isDeleted=False)
                .filter(or_(
                    User.userName==username,
                    and_(
                        User.phoneNumber==phoneNumber,
                        User.country_code==country_code,
                    ),
                    and_(
                        User.emailAddress==email,
                        User.emailAddress.isnot(None),
                    ),
                ))
                .first()
            )

            if alreadyExist is not None:
                resp = Response(
                    json.dumps({
                        "status": False,
                        "Message": "Username, email or phone number already exists"}
                    ),
                    status=500,
                )
            else:
                last_login = datetime.utcnow()
                new_user = User(
                    firstName=first_name,
                    lastName=last_name,
                    userName=username,
                    avatarUrl=None,
                    phoneNumber=None,
                    emailAddress=email,
                    gender=None,
                    city=0,
                    birthDate=None,
                    birthPlace=None,
                    lastLogin=last_login,
                    password=password,
                    flagUrl="",
                    locale=locale,
                    phone_number=phone_number,
                )
                session.add(new_user)
                session.flush()

                code = randint(100000, 999999)
                verify = Verification(user=new_user, code=code)
                session.add(verify)

                send_verify_sms(new_user, verify.code)

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
        resp = {"message": "Something is Wrong!"}

        try:

            if "username" in request.form.keys():
                username = request.form["username"].lower()
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
                session.query(User)
                .filter_by(isDeleted=False)
                .filter_by(userName=username)
                .first()
            )
            if user is not None:
                if user.validate_password(password):
                    if not user.isVerified:
                        verify = session.query(Verification) \
                            .filter_by(user_id=user.id) \
                            .first()

                        if verify is None:
                            verify = Verification(user=user)
                            session.add(verify)

                        verify.code = randint(100000, 999999)
                        verify.expire_at = datetime.utcnow() + timedelta(
                            minutes=app.config['VERIFICATION_EMAIL_MAXAGE']
                        )

                        session.commit()
                        send_verify_email(user, verify.code)

                        resp = make_response(
                            jsonify({
                                'user': obj_to_dict(user),
                            }),
                            302,
                        )
                        return

                    lang = get_locale()
                    user.locale = Locale(lang)
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
                    json.dumps({"message": "Please Register First"}), status=400
                )

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": str(e)}), status=400)

        finally:
            session.close()
            return resp


class LogoutAccess(Resource):
    @authorize
    @swag_from("./docs/auth/logout-access.yml")
    def post(self):
        jti = get_raw_jwt()['jti']
        msg = None
        try:
            revoked_token = RevokedToken(jti=jti)
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
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
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
        resp = {"message": "Something is Wrong"}, 500

        try:
            user_id = int(user_id)
            user = session.query(User).filter_by(id=user_id).first()
            if user is None:
                resp = {"message": "Something is Wrong"}, 500
                return

            verify = session.query(Verification).filter_by(user_id=user_id).first()
            sent_verify_code = request.form.get('verifyCode', 'invalid')

            if user.isVerified:
                resp = {"message": "User Already verified"}, 600
                return

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
        resp = {"message": "Something is Wrong"}

        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user.isVerified:
                resp = Response(
                    json.dumps({"message": "User is already verified."}), status=200
                )
                return

            verify = session.query(Verification).filter_by(user_id=user_id).first()
            if verify is None:
                verify = Verification(user=user)
                session.add(verify)

            verify.code = randint(100000, 999999)
            verify.expire_at = datetime.utcnow() + timedelta(
                minutes=app.config['VERIFICATION_MAXAGE']
            )

            session.commit()
            send_verify_sms(user, verify.code)
            resp = Response(
                json.dumps({"message": "Verification Code Sent."}),
                status=200,
            )

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
        id = get_jwt_identity()
        user = session.query(User).get(id)
        session.close()
        access_token = create_user_access_token(user, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'accessToken': f'Bearer {access_token}',
            "refreshToken": f"Bearer {refresh_token}",
        })


class ResetPasswordApi(Resource):

    decorators = [limiter.limit("2/minute")]

    @commit
    @swag_from("./docs/auth/reset_password.yml")
    def post(self):

        email = request.form.get('email').lower()
        language = get_locale()
        if not email:
            return make_response({'message': 'email is missing'}, 400)

        user = session.query(User) \
            .filter_by(emailAddress=email) \
            .first()

        if user:
            reset_password = ResetPassword(user=user)
            session.add(reset_password)
            session.flush()
            reset_password.send_email(language)

        return make_response({'message': 'reset password email sent, maybee'})


class ConfirmResetPassword(Resource):

    decorators = [limiter.limit("2/minute")]

    @commit
    @swag_from("./docs/auth/confirm_reset_password.yml")
    def post(self, token):

        reset_password = session.query(ResetPassword) \
            .filter_by(token=token) \
            .filter(ResetPassword.is_used==False) \
            .filter(ResetPassword.is_expired==False) \
            .first()

        if reset_password is None:
            return make_response({'message': 'Bad request'}, 400)

        new_password = request.form['password']
        confirm_new_password = request.form['confirm_password']
        if new_password != confirm_new_password:
            return make_response({'message': 'passwords dose not match'}, 499)

        user = session.query(User).get(reset_password.user_id)

        user.password = new_password
        reset_password.is_used = True

        access_token = create_user_access_token(user)
        refresh_token = create_refresh_token(identity=user.id)

        resp = make_response(
            {
                'message': 'Password Changed Successfully',
                'accessToken': f'Bearer {access_token}',
                'refreshToken': f'Bearer {refresh_token}',
                'user': obj_to_dict(user),
            },
        )

        return resp

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
api.add_resource(ResetPasswordApi, "/api/v2/auth/password/reset")
api.add_resource(
    ConfirmResetPassword,
    "/api/v2/auth/password/reset/confirm/token=<token>",
)
