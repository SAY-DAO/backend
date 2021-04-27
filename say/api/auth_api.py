from datetime import datetime
from datetime import timedelta

import phonenumbers
from babel import Locale
from email_validator import EmailNotValidError
from email_validator import validate_email
from flasgger import swag_from
from flask import request
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_raw_jwt
from flask_restful import Resource
from sqlalchemy_utils import Country
from sqlalchemy_utils import PhoneNumber
from sqlalchemy_utils import PhoneNumberParseException

from say.exceptions import HTTPException
from say.models import EmailVerification
from say.models import PhoneVerification
from say.models import ResetPassword
from say.models import User
from say.models import Verification
from say.models import and_
from say.models import commit
from say.models import or_
from say.orm import obj_to_dict
from say.orm import safe_commit
from say.orm import session
from say.tasks import subscribe_email
from say.validations import validate_password
from say.validations import validate_phone
from say.validations import validate_username

from ..authorization import authorize
from ..authorization import authorize_refresh
from ..authorization import create_user_access_token
from ..authorization import revoke_jwt
from ..config import configs
from ..decorators import json
from ..i18n import t
from ..locale import get_locale
from ..schema.user import NewUserSchema
from .ext import api
from .ext import limiter


'''
Authentication APIs
'''


def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()


class RegisterUser(Resource):

    @json
    @commit
    @swag_from('./docs/auth/register.yml')
    def post(self):
        try:
            data = NewUserSchema(**request.form.to_dict())
        except ValueError as e:
            return e.json(), 400

        username = data.username

        phone_number = None
        if 'phoneNumber' in request.form.keys():
            phone_number = request.form['phoneNumber']
            phone_number = phone_number.replace(' ', '')
            if phone_number == '':
                phone_number = None

        if 'countryCode' in request.form.keys() and request.form['countryCode']:
            country = request.form['countryCode']
            try:
                country = Country(country.upper())
            except ValueError:
                return {'message': 'Invalid countryCode'}, 400
        else:
            country = None

        if 'password' in request.form.keys():
            password = request.form['password']
            if not validate_password(password):
                return {
                           'message': 'password must be at least 6 charachters'}, 400

        else:
            return {'message': 'password is needed'}, 400

        email = None
        if 'email' in request.form.keys():
            email = request.form['email'].lower()
            if bool(email) == False:
                email = None

        if not email and not phone_number:
            return {'message': 'Email or Phone Number is required'}, 400

        if 'verifyCode' in request.form.keys():
            code = request.form['verifyCode']
        else:
            return {'message': 'verifyCode is needed'}, 400

        if 'isInstalled' in request.form.keys():
            is_installed = bool(
                int(request.form['isInstalled'])
            )
        else:
            return {'message': 'isInstalled is needed'}, 400

        lang = get_locale()
        locale = Locale(lang)

        if phone_number and not validate_phone(phone_number):
            return {'message': 'Invalid phoneNumber'}, 400

        if not validate_username(username):
            return {'message': 'Invalid username'}, 400

        if email and not validate_email(email):
            return {'message': 'Invalid email'}, 400

        code = code.replace('-', '')

        alreadyExist = (
            session.query(User)
                .filter_by(isDeleted=False)
                .filter(or_(
                User.formated_username == username.lower(),
                and_(
                    User.phone_number == phone_number,
                    User.phone_number.isnot(None),
                    User.phone_number != '',
                ),
                and_(
                    User.emailAddress == email,
                    User.emailAddress.isnot(None),
                ),
            ))
                .first()
        )

        if alreadyExist is not None:
            return (
                {'message': 'Username, email or phone number already exists'},
                422,
            )

        verification = session.query(Verification) \
            .filter(Verification._code == code) \
            .filter(Verification.verified.is_(True)) \
            .filter(or_(
            EmailVerification.email == email,
            PhoneVerification.phone_number == phone_number,
        )) \
            .one_or_none()

        if not verification:
            return {'message': 'Invalid verifyCode'}, 400

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
            is_nakama=False,
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
            'message': 'User successfully created',
            'accessToken': f'Bearer {access_token}',
            'refreshToken': f'Bearer {refresh_token}',
            'user': obj_to_dict(new_user),
        }

        if new_user.emailAddress:
            subscribe_email.delay(
                configs.MAILERLITE_GROUP_ID,
                dict(email=new_user.emailAddress),
            )

        return resp


class Login(Resource):
    decorators = [limiter.limit('10/minute')]

    @json
    @swag_from('./docs/auth/login.yml')
    def post(self):
        if 'username' in request.form.keys():
            username = request.form['username'].lower()
        else:
            return {'message': 'userName is needed'}, 400

        if 'password' in request.form.keys():
            password = request.form['password']
        else:
            return {'message': 'password is needed'}, 400

        if 'isInstalled' in request.form.keys():
            is_installed = bool(int(request.form['isInstalled']))
        else:
            return {'message': 'isInstalled is needed'}, 400

        user_query = session.query(User).filter_by(isDeleted=False)

        user = None
        try:
            user = user_query \
                .filter(and_(
                    User.phone_number == username,
                    User.is_phonenumber_verified == True,
                )).one_or_none()
        except phonenumbers.phonenumberutil.NumberParseException:
            pass
        if user is None:
            user = user_query \
                .filter(or_(
                    and_(
                        User.emailAddress == username,
                        User.is_email_verified == True,
                    ),
                    User.formated_username == username,
                )).one_or_none()

        if user is None:
            return {'message': 'Please Register First'}, 400

        if not user.validate_password(password):
            return {'message': 'Username or Password is Wrong'}, 400

        lang = get_locale()
        user.locale = Locale(lang)
        user.lastLogin = datetime.utcnow()
        user.is_installed = is_installed
        safe_commit(session)

        access_token = create_user_access_token(user)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'message': 'Login Successful',
            'accessToken': f'Bearer {access_token}',
            'refreshToken': f'Bearer {refresh_token}',
            'user': obj_to_dict(user),
        }


class LogoutAccess(Resource):
    @authorize
    @swag_from('./docs/auth/logout-access.yml')
    def post(self):
        jti = get_raw_jwt()['jti']
        revoke_jwt(jti, int(configs.JWT_ACCESS_TOKEN_EXPIRES * 1.1))
        return {}, 200


class LogoutRefresh(Resource):
    @authorize_refresh
    @swag_from('./docs/auth/logout-refresh.yml')
    def post(self):
        jti = get_raw_jwt()['jti']
        revoke_jwt(jti, int(configs.JWT_REFRESH_TOKEN_EXPIRES * 1.1))
        return {}, 200


class VerifyPhone(Resource):
    decorators = [limiter.limit('5/minute')]

    @json
    @commit
    @swag_from('./docs/verification/verify-phone.yml')
    def post(self):
        phone_number = request.form.get('phone_number', None)

        if not phone_number:
            return {'message': 'phone_number is required'}, 400

        try:
            phone_number = PhoneNumber(phone_number)
        except PhoneNumberParseException:
            return {'message': 'phone_number is invalid'}, 400

        user = session.query(User) \
            .filter(User.phone_number == phone_number) \
            .first()

        if user:
            return {'message': 'phone_number already exixst'}, 422

        verification = PhoneVerification(
            phone_number=phone_number,
            expire_at=datetime.utcnow() + timedelta(
                minutes=configs.VERIFICATION_MAXAGE,
            ),
        )
        session.add(verification)
        session.flush()
        verification.send()

        return verification


class VerificationAPI(Resource):
    decorators = [
        limiter.limit('5/minute', error_message=t('verification.too_many')),
    ]

    @json
    @commit
    @swag_from('./docs/verification/verify.yml')
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
    decorators = [limiter.limit('5/minute')]

    @json
    @commit
    @swag_from('./docs/verification/verify-email.yml')
    def post(self):
        email = request.form.get('email', None)

        if not email:
            return {'message': 'email is required'}, 400

        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            return {'message': 'email is invalid'}, 400

        user = session.query(User) \
            .filter(and_(
                User.emailAddress == email,
            )).first()

        if user:
            return {'message': 'email already exixst'}, 422

        verification = EmailVerification(
            email=email,
            expire_at=datetime.utcnow() + timedelta(
                minutes=configs.VERIFICATION_MAXAGE,
            ),
        )
        session.add(verification)
        session.flush()
        verification.send()

        return verification


class TokenRefresh(Resource):

    @authorize_refresh
    @json
    @swag_from('./docs/auth/refresh.yml')
    def post(self):
        id = get_jwt_identity()
        user = session.query(User).get(id)
        session.close()
        access_token = create_user_access_token(user, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)

        jti = get_raw_jwt()['jti']
        revoke_jwt(jti, int(configs.JWT_REFRESH_TOKEN_EXPIRES * 1.1))

        return {
            'accessToken': f'Bearer {access_token}',
            'refreshToken': f'Bearer {refresh_token}',
        }


class ResetPasswordByEmailApi(Resource):
    decorators = [limiter.limit('2/minute')]

    @json
    @commit
    @swag_from('./docs/auth/reset_password_by_email.yml')
    def post(self):

        email = request.form.get('email').lower()

        if not email:
            return {'message': 'email is missing'}, 400

        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            return {'message': 'email is invalid'}, 400

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
            language = get_locale()
            reset_password.send_email(language)

        return {'message': 'reset password token sent, maybee'}


class ResetPasswordByPhoneApi(Resource):
    decorators = [limiter.limit('2/minute')]

    @json
    @commit
    @swag_from('./docs/auth/reset_password_by_phone.yml')
    def post(self):

        phone_number = request.form.get('phoneNumber')
        language = get_locale()

        if not phone_number:
            return {'message': 'phoneNumber is missing'}, 400

        try:
            phonenumbers.parse(phone_number)
        except phonenumbers.phonenumberutil.NumberParseException:
            return {'message': 'phone is invalid'}, 400

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

        return {'message': 'reset password code sent, maybee'}


class ConfirmResetPassword(Resource):
    decorators = [limiter.limit('2/minute')]

    @json
    @commit
    @swag_from('./docs/auth/confirm_reset_password.yml')
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
            return {'message': 'passwords dose not match'}, 499

        user = session.query(User).get(reset_password.user_id)

        user.password = new_password
        reset_password.is_used = True

        access_token = create_user_access_token(user)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'message': 'Password Changed Successfully',
            'accessToken': f'Bearer {access_token}',
            'refreshToken': f'Bearer {refresh_token}',
            'user': obj_to_dict(user),
        }


api.add_resource(RegisterUser, '/api/v2/auth/register')
api.add_resource(Login, '/api/v2/auth/login')
api.add_resource(LogoutAccess, '/api/v2/auth/logout/token')
api.add_resource(LogoutRefresh, '/api/v2/auth/logout/refresh')
api.add_resource(TokenRefresh, '/api/v2/auth/refresh')
api.add_resource(VerifyPhone, '/api/v2/auth/verify/phone')
api.add_resource(VerifyEmail, '/api/v2/auth/verify/email')
api.add_resource(VerificationAPI, '/api/v2/auth/verify/<int:id>')
api.add_resource(ResetPasswordByEmailApi, '/api/v2/auth/password/reset/email')
api.add_resource(ResetPasswordByPhoneApi, '/api/v2/auth/password/reset/phone')
api.add_resource(
    ConfirmResetPassword,
    '/api/v2/auth/password/reset/confirm/token=<token>',
)
