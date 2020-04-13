from . import *
from say.models import User, session
from say.validations import validate_username, validate_email, validate_phone


'''
Check APIs
'''


class CheckUsername(Resource):

    @json
    @swag_from('./docs/check/username.yml')
    def get(self, username):
        if not validate_username(username):
            return {'message': 'Invalid Username'}, 710

        user = session.query(User) \
            .filter_by(formated_username=username.lower()) \
            .one_or_none()

        if user:
            return {'message': 'Username Exists'}, 711

        return {'message': 'Username is avaliable'}, 200


class CheckEmail(Resource):

    @json
    @swag_from('./docs/check/email.yml')
    def get(self, email):
        if not validate_email(email):
            return {'message': 'Invalid Email'}, 720

        user = session.query(User) \
            .filter_by(emailAddress=email.lower()) \
            .one_or_none()

        if user:
            return {'message': 'Email Exists'}, 721

        return {'message': 'Email is avaliable'}, 200


class CheckPhone(Resource):

    @json
    @swag_from('./docs/check/phone.yml')
    def get(self, phone):
        if not validate_phone(phone):
            return {'message': 'Invalid Phone'}, 730

        user = session.query(User) \
            .filter_by(phone_number=phone) \
            .one_or_none()

        if user:
            return {'message': 'Phone Exists'}, 731

        return {'message': 'Phone is avaliable'}, 200


api.add_resource(CheckUsername, '/api/v2/check/username/<username>')
api.add_resource(CheckEmail, '/api/v2/check/email/<email>')
api.add_resource(CheckPhone, '/api/v2/check/phone/<phone>')

