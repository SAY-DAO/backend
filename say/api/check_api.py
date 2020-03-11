from . import *
from say.models import User, session
from say.validations import username_validator


'''
Check APIs
'''


class CheckUsername(Resource):

    @json
    @swag_from('./docs/check/username.yml')
    def get(self, username):
        if not username_validator(username):
            return {'message': 'Invalid Username'}, 400

        user = session.query(User).filter_by(userName=username).one_or_none()
        if user:
            return {'message': 'Username Exists'}, 422

        return {'message': 'Username is avaliable'}, 200


api.add_resource(CheckUsername, '/api/v2/check/username/<username>')
