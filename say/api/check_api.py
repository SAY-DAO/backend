from . import *
from say.models import User, session
from say.validations import username_validator, email_validator, phone_validator


'''
Check APIs
'''


class CheckUsername(Resource):

    @json
    @swag_from('./docs/check/username.yml')
    def get(self, username):
        if not username_validator(username):
            return {'message': 'Invalid Username'}, 400

        user = session.query(User) \
            .filter_by(formated_username=username.lower()) \
            .one_or_none()

        if user:
            return {'message': 'Username Exists'}, 422

        return {'message': 'Username is avaliable'}, 200


class CheckEmail(Resource):

    @json
    @swag_from('./docs/check/email.yml')
    def get(self, email):
        if not email_validator(email):
            return {'message': 'Invalid Email'}, 400

        user = session.query(User) \
            .filter_by(emailAddress=email.lower()) \
            .one_or_none()

        if user:
            return {'message': 'Email Exists'}, 422

        return {'message': 'Email is avaliable'}, 200


class CheckPhone(Resource):

    @json
    @swag_from('./docs/check/phone.yml')
    def get(self, phone):
        if not phone_validator(phone):
            return {'message': 'Invalid Phone'}, 400

        user = session.query(User) \
            .filter_by(phone_number=phone) \
            .one_or_none()

        if user:
            return {'message': 'Phone Exists'}, 422

        return {'message': 'Phone is avaliable'}, 200


api.add_resource(CheckUsername, '/api/v2/check/username/<username>')
api.add_resource(CheckEmail, '/api/v2/check/email/<email>')
api.add_resource(CheckPhone, '/api/v2/check/phone/<phone>')

