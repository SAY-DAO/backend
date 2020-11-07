import phonenumbers
from babel import Locale
from flask_jwt_extended import create_refresh_token, get_raw_jwt
from sqlalchemy_utils import PhoneNumber, Country, PhoneNumberParseException

from say.models import session, or_, commit, ResetPassword, \
    PhoneVerification, Verification, EmailVerification, User, and_
from say.tasks import subscribe_email
from say.validations import validate_username, validate_email, validate_phone, \
    validate_password
from say.orm import safe_commit
from ..i18n import t
from . import *
from .exception import HTTPException
from ..schema.user import NewUserSchema

"""
Authentication APIs
"""


def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()


class RegisterUser(Resource):

    @json
    @commit
    @swag_from("./docs/auth/register.yml")
    def post(self):
        try:
            data = NewUserSchema(**request.form.to_dict())
        except ValueError as e:
            return e.json(), 400

        username = data.username

        phoneNumber = None
        if "phoneNumber" in request.form.keys():
            phoneNumber = request.form["phoneNumber"]
            phone_number = phoneNumber.replace(' ', '')
            if phone_number == '':
                phone_number = None

        if "countryCode" in request.form.keys() and request.form['countryCode']:
            country = request.form["countryCode"]
            try:
                country = Country(country.upper())
            except ValueError:
                return {"message": "Invalid countryCode"}, 400
        else:
           country = None

        if "password" in request.form.keys():
            password = request.form["password"]
            if not validate_password(password):
                return {"message": "password must be at least 6 charachters"}, 400

        else:
            return {"message": "password is needed"}, 400

        email = None
        if "email" in request.form.keys():
            email = request.form["email"].lower()
            if bool(email) == False:
                email = None

        if not email and not phoneNumber:
            return {'message': 'Email or Phone Number is required'}, 400

        if "verifyCode" in request.form.keys():
            code = request.form["verifyCode"]
        else:
            return {"message": "verifyCode is needed"}, 400

        if "isInstalled" in request.form.keys():
            is_installed = bool(
                int(request.form["isInstalled"])
            )
        else:
            return {"message": "isInstalled is needed"}, 400

        lang = get_locale()
        locale = Locale(lang)

        if phoneNumber and not validate_phone(phone_number):
            return {"message": "Invalid phoneNumber"}, 400

        if not validate_username(username):
            return {"message": "Invalid username"}, 400

        if email and not validate_email(email):
            return {"message": "Invalid email"}, 400

        code = code.replace('-', '')

        alreadyExist = (
            session.query(User)
            .filter_by(isDeleted=False)
            .filter(or_(
                User.formated_username==username.lower(),
                and_(
                    User.phone_number==phone_number,
                    User.phone_number.isnot(None),
                    User.phone_number!='',
                ),
                and_(
                    User.emailAddress==email,
                    User.emailAddress.isnot(None),
                ),
            ))
            .first()
        )

        if alreadyExist is not None:
            return (
                {"message": "Username, email or phone number already exists"},
                422,
            )

        verification = session.query(Verification) \
            .filter(Verification._code==code) \
            .filter(Verification.verified.is_(True)) \
            .filter(or_(
                EmailVerification.email==email,
                PhoneVerification.phone_number==phone_number,
            )) \
            .one_or_none()

        if not verification:
            return {"message": "Invalid verifyCode"}, 400

        last_login = datetime.utcnow()
        new_user = User(
            firstName='',
            lastName='',
            userName=username,
            avatarUrl=None,
            emailAddress=email,
            gender=None,
            city=0,
            birthDate=None,
            birthPlace=None,
            lastLogin=last_login,
            password=password,
            locale=locale,
            phone_number=phone_number,
            country=country,
            is_installed=is_installed,
        )
        session.add(new_user)

        if isinstance(verification, EmailVerification):
            new_user.is_email_verified = True
        else:
            new_user.is_phonenumber_verified = True

        session.flush()
        access_token = create_user_access_token(new_user)
        refresh_token = create_refresh_token(identity=new_user.id)

        resp = {
            "message": "User successfully created",
            "accessToken": f"Bearer {access_token}",
            "refreshToken": f"Bearer {refresh_token}",
            "user": obj_to_dict(new_user),
        }

        if new_user.emailAddress:
            subscribe_email.delay(
                app.config.get('MAILERLITE_GROUP_ID', 'not-entered'),
                dict(email=new_user.emailAddress),
            )

        return resp


class Login(Resource):

    @swag_from("./docs/auth/login.yml")
    def post(self):
        resp = {"message": "Something is Wrong!"}
        try:

            if "username" in request.form.keys():
                username = request.form["username"].lower()
            else:
                resp = make_response(
                    jsonify({"message": "userName is needed"}), 500
                )
                return

            if "password" in request.form.keys():
                password = request.form["password"]
            else:
                resp = make_response(
                    jsonify({"message": "password is needed"}), 500
                )
                return

            if "isInstalled" in request.form.keys():
                is_installed = bool(int(request.form["isInstalled"]))
            else:
                resp = {"message": "isInstalled is needed"}, 400
                return

            user_query = session.query(User).filter_by(isDeleted=False)

            user = None
            try:
                user = user_query \
                    .filter(and_(
                        User.phone_number==username,
                        User.is_phonenumber_verified==True,
                    )).first()

            except phonenumbers.phonenumberutil.NumberParseException:
                user = user_query \
                    .filter(or_(
                        and_(
                            User.emailAddress==username,
                            User.is_email_verified==True,
                        ),
                        User.formated_username==username,
                    )).first()

            if user is None:
                resp = make_response(
                    jsonify({"message": "Please Register First"}), 400
                )
                return

            if not user.validate_password(password):
                resp = make_response(
                    jsonify({"message": "Username or Password is Wrong"}),
                    400,
                )
                return
            
            lang = get_locale()
            user.locale = Locale(lang)
            user.lastLogin = datetime.utcnow()
            user.is_installed = is_installed
            safe_commit(session)

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

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": str(e)}), 400)

        finally:
            session.close()
            return resp


class LogoutAccess(Resource):
    @authorize
    @swag_from("./docs/auth/logout-access.yml")
    def post(self):
        jti = get_raw_jwt()['jti']
        revoke_jwt(jti, int(app.config['JWT_ACCESS_TOKEN_EXPIRES'] * 1.1))
        return {}, 200


class LogoutRefresh(Resource):
    @authorize_refresh
    @swag_from("./docs/auth/logout-refresh.yml")
    def post(self):
        jti = get_raw_jwt()['jti']
        revoke_jwt(jti, int(app.config['JWT_REFRESH_TOKEN_EXPIRES'] * 1.1))
        return {}, 200


class VerifyPhone(Resource):
    decorators = [limiter.limit("5/minute")]

    @json
    @commit
    @swag_from("./docs/verification/verify-phone.yml")
    def post(self):
        phone_number = request.form.get('phone_number', None)

        if not phone_number:
            return {"message": "phone_number is required"}, 400

        try:
            phone_number = PhoneNumber(phone_number)
        except PhoneNumberParseException:
            return {"message": "phone_number is invalid"}, 400

        user = session.query(User) \
            .filter(User.phone_number == phone_number) \
            .first()

        if user:
            return {"message": "phone_number already exixst"}, 422

        verification = PhoneVerification(
            phone_number=phone_number,
            expire_at=datetime.utcnow() + timedelta(
                minutes=app.config['VERIFICATION_MAXAGE'],
            ),
        )
        session.add(verification)
        session.flush()
        verification.send()

        return verification

    
class VerificationAPI(Resource):
    decorators = [limiter.limit("5/minute", error_message=t('verification.too_many'))]

    @json
    @commit
    @swag_from("./docs/verification/verify.yml")
    def patch(self, id):
        code = request.form.get('code')
        code = code.replace('-', '')

        verification = session.query(Verification).get(id)

        if not verification:
            raise HTTPException(404, t('verification.4o4'))

        if verification._code != code:
            raise HTTPException(400, t('verification.invalid'))

        if verification.is_expired:
            raise HTTPException(400, t('verification.expired'))

        verification.verified = True
        return {'message': 'ok'}


class VerifyEmail(Resource):
    decorators = [limiter.limit("5/minute")]

    @json
    @commit
    @swag_from("./docs/verification/verify-email.yml")
    def post(self):
        email = request.form.get('email', None)

        if not email:
            return {"message": "email is required"}, 400

        user = session.query(User) \
            .filter(and_(
                User.emailAddress==email,
                User.is_email_verified==True,
            )).first()

        if user:
            return {"message": "email already exixst"}, 422

        verification = EmailVerification(
            email=email,
            expire_at=datetime.utcnow() + timedelta(
                minutes=app.config['VERIFICATION_MAXAGE'],
            ),
        )
        session.add(verification)
        session.flush()
        verification.send()

        return verification


class TokenRefresh(Resource):

    @authorize_refresh
    @swag_from("./docs/auth/refresh.yml")
    def post(self):
        id = get_jwt_identity()
        user = session.query(User).get(id)
        session.close()
        access_token = create_user_access_token(user, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)

        jti = get_raw_jwt()['jti']
        revoke_jwt(jti, int(app.config['JWT_REFRESH_TOKEN_EXPIRES'] * 1.1))

        return jsonify({
            'accessToken': f'Bearer {access_token}',
            "refreshToken": f"Bearer {refresh_token}",
        })


class ResetPasswordByEmailApi(Resource):

    decorators = [limiter.limit("2/minute")]

    @commit
    @swag_from("./docs/auth/reset_password_by_email.yml")
    def post(self):

        email = request.form.get('email').lower()
        language = get_locale()
        if not email:
            return make_response({'message': 'email is missing'}, 400)

        user = session.query(User) \
            .filter_by(emailAddress=email) \
            .first()

        if user:
            session.query(ResetPassword) \
                .filter(ResetPassword.user_id == user.id) \
                .update({'is_used': True})

            reset_password = ResetPassword(user=user)
            session.add(reset_password)
            session.flush()
            reset_password.send_email(language)

        return make_response({'message': 'reset password token sent, maybee'})


class ResetPasswordByPhoneApi(Resource):

    decorators = [limiter.limit("2/minute")]

    @commit
    @swag_from("./docs/auth/reset_password_by_phone.yml")
    def post(self):

        phone_number = request.form.get('phoneNumber')
        language = get_locale()
        if not phone_number:
            return make_response({'message': 'phoneNumber is missing'}, 400)

        user = session.query(User) \
            .filter_by(phone_number=phone_number) \
            .first()

        if user:
            session.query(ResetPassword) \
                .filter(ResetPassword.user_id == user.id) \
                .update({'is_used': True})

            reset_password = ResetPassword(user=user)
            session.add(reset_password)
            session.flush()
            reset_password.send_sms(language)

        return make_response({'message': 'reset password code sent, maybee'})


class ConfirmResetPassword(Resource):

    decorators = [limiter.limit("2/minute")]

    @commit
    @swag_from("./docs/auth/confirm_reset_password.yml")
    def post(self, token):

        reset_password = session.query(ResetPassword) \
            .filter_by(token=token) \
            .first()

        if reset_password is None:
            raise HTTPException(404, t('reset_password.4o4'))
        elif reset_password.is_used:
            raise HTTPException(400, t('reset_password.used'))
        elif reset_password.is_expired:
            raise HTTPException(400, t('reset_password.expired'))

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


api.add_resource(RegisterUser, "/api/v2/auth/register")
api.add_resource(Login, "/api/v2/auth/login")
api.add_resource(LogoutAccess, "/api/v2/auth/logout/token")
api.add_resource(LogoutRefresh, "/api/v2/auth/logout/refresh")
api.add_resource(TokenRefresh, "/api/v2/auth/refresh")
api.add_resource(VerifyPhone, "/api/v2/auth/verify/phone")
api.add_resource(VerifyEmail, "/api/v2/auth/verify/email")
api.add_resource(VerificationAPI, "/api/v2/auth/verify/<int:id>")
api.add_resource(ResetPasswordByEmailApi, "/api/v2/auth/password/reset/email")
api.add_resource(ResetPasswordByPhoneApi, "/api/v2/auth/password/reset/phone")
api.add_resource(
    ConfirmResetPassword,
    "/api/v2/auth/password/reset/confirm/token=<token>",
)
