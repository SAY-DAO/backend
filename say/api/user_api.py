import functools
import os
from datetime import datetime
from random import randint

from flasgger import swag_from
from flask import request
from flask_restful import Resource
from sqlalchemy import func
from werkzeug.utils import secure_filename

from say.gender import Gender
from say.models import obj_to_dict
from say.models.family_model import Family
from say.models.need_family_model import NeedFamily
from say.models.user_family_model import UserFamily
from say.models.user_model import User
from say.orm import safe_commit, session
from say.validations import validate_email, validate_phone, allowed_image
from .ext import api
from ..authorization import get_user_role, get_user_id, authorize
from ..config import configs
from ..decorators import json
from ..exceptions import HTTP_PERMISION_DENIED, HTTP_NOT_FOUND
from ..roles import *
from ..schema.user import UserNameSchema, UserSearchSchema

'''
User APIs
'''


def is_int(maybe_int):
    try:
        int(maybe_int)
        return True
    except (ValueError, TypeError):
        return False


def me_or_user_id(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_id = kwargs['user_id']
        user_role = get_user_role()

        if user_id == 'me' and user_role == USER:
            user_id = get_user_id()
        elif is_int(user_id) and user_role in [ADMIN, SUPER_ADMIN]:
            user_id = int(user_id)
        else:
            raise HTTP_PERMISION_DENIED()

        kwargs['user_id'] = user_id
        return func(*args, **kwargs)

    return wrapper


class GetUserById(Resource):

    @authorize(USER, ADMIN, SUPER_ADMIN)
    @me_or_user_id
    @json
    @swag_from('./docs/user/by_id.yml')
    def get(self, user_id):
        user = (
            session.query(User)
            .filter_by(id=user_id)
            .filter_by(isDeleted=False)
            .first()
        )
        return user


class GetUserChildren(Resource):

    @authorize(USER, ADMIN, SUPER_ADMIN)
    @me_or_user_id
    @json
    @swag_from('./docs/user/children.yml')
    def get(self, user_id):
        user = session.query(User).get(user_id)
        if user.isDeleted:
            raise HTTP_NOT_FOUND()

        children = []
        for family_member in user.user_families:
            child = family_member.family.child
            if not child.isConfirmed and get_user_role() in [USER]:
                continue

            children.append(obj_to_dict(child))

        result = dict(
            total_count=len(children),
            children=children,
        )
        return result


class UpdateUserById(Resource):

    @authorize(USER, ADMIN, SUPER_ADMIN)
    @me_or_user_id
    @json
    @swag_from('./docs/user/update.yml')
    def patch(self, user_id):
        primary_user = (
            session.query(User)
            .filter_by(id=user_id)
            .filter_by(isDeleted=False)
            .first()
        )

        if 'avatarUrl' in request.files.keys():
            file = request.files['avatarUrl']
            if file.filename == '':
                return {'message': 'ERROR OCCURRED --> EMPTY FILE!'}, 400

            if file and allowed_image(file.filename):
                filename = secure_filename(file.filename)
                filename = str(primary_user.id) + '.' + filename.split('.')[-1]

                temp_user_path = os.path.join(
                    configs.UPLOAD_FOLDER,
                    str(primary_user.id) + '-user',
                )

                if not os.path.isdir(temp_user_path):
                    os.makedirs(temp_user_path, exist_ok=True)

                for obj in os.listdir(temp_user_path):
                    check = str(primary_user.id) + '-avatar'
                    if obj.split('_')[0] == check:
                        os.remove(os.path.join(temp_user_path, obj))

                primary_user.avatarUrl = os.path.join(
                    temp_user_path,
                    str(primary_user.id) + str(randint(1000, 100000)) + '-avatar_' + filename,
                )
                file.save(primary_user.avatarUrl)
                primary_user.avatarUrl = '/' + primary_user.avatarUrl

        raw_username = request.form.get('userName', primary_user.userName)
        if raw_username != primary_user.userName:
            try:
                username = UserNameSchema(username=raw_username).username
            except ValueError as ex:
                resp = ex.json(), 400
                return resp

            username_exist = session.query(User.id) \
                .filter(User.formated_username==username.lower()) \
                .filter(User.id!=primary_user.id) \
                .filter(User.isDeleted==False) \
                .scalar()

            if username_exist:
                return {'message': 'Username exists'}, 400

            primary_user.userName = username

        if (email := request.form.get('emailAddress')) and \
                not primary_user.is_email_verified:

            if not validate_email(email):
                return {'message': 'Invalid email'}, 400

            email_exist = session.query(User.id) \
                .filter(func.lower(User.emailAddress)==email.lower()) \
                .filter(User.id!=primary_user.id) \
                .filter(User.isDeleted==False) \
                .scalar()

            if email_exist:
                return {'message': 'Email exists'}

            primary_user.emailAddress = email

        if 'password' in request.form.keys():
            primary_user.password = request.form['password']

        if 'firstName' in request.form.keys():
            primary_user.firstName = request.form['firstName']

        if 'lastName' in request.form.keys():
            primary_user.lastName = request.form['lastName']

        if 'country_code' in request.form.keys():
            primary_user.country_code = request.form['country_code']

        if 'city' in request.form.keys():
            primary_user.city = int(request.form['city'])

        if 'postal_address' in request.form.keys():
            primary_user.postal_address = request.form['postal_address']

        if 'postal_code' in request.form.keys():
            postal_code_temp = request.form['postal_code']
            if is_int(postal_code_temp) and len(postal_code_temp) == 10:
                primary_user.postal_code = postal_code_temp
            else:
                return dict(
                    message='Invalid postal code, it must have exactly 10 digits without dash.'
                ), 498

        if 'birthPlace' in request.form.keys():
            primary_user.birthPlace = int(request.form['birthPlace'])

        if 'locale' in request.form.keys():
            primary_user.locale = request.form['locale'].lower()

        if (phone := request.form.get('phoneNumber')) and \
                not primary_user.is_phonenumber_verified:

            if not validate_phone(phone):
                return {'message': 'Invalid phone'}, 400

            phone_exist = session.query(User.id) \
                .filter(User.phone_number==phone) \
                .filter(User.id!=primary_user.id) \
                .filter(User.isDeleted==False) \
                .scalar()

            if phone_exist:
                return {'message': 'Phone exists'}, 400

            primary_user.phone_number = phone

        if 'birthDate' in request.form.keys():
            primary_user.birthDate = datetime.strptime(
                request.form['birthDate'],
                '%Y-%m-%d'
            )

        if 'gender' in request.form.keys():
            gender = request.form['gender']
            if not hasattr(Gender, gender):
                return dict(
                    message=f'Invalid gender, only can selected in '
                            f'{Gender.__members__.keys()}',
                    ), 498

            primary_user.gender = request.form['gender']

        secondary_user = obj_to_dict(primary_user)

        safe_commit(session)
        return secondary_user


class DeleteUserById(Resource):
    @authorize(ADMIN, SUPER_ADMIN)
    @json
    @swag_from('./docs/user/delete.yml')
    def patch(self, user_id):
        user = session.query(User).get(user_id)

        if user.isDeleted:
            return {'message': 'user was already deleted!'}, 400

        families = (
            session.query(UserFamily)
            .filter_by(id_user=user_id)
            .filter_by(isDeleted=False)
            .all()
        )
        needs = (
            session.query(NeedFamily)
            .filter_by(id_user=user_id)
            .filter_by(isDeleted=False)
            .all()
        )

        for family in families:
            family.isDeleted = True

        for need in needs:
            need.isDeleted = True

        user.isDeleted = True
        safe_commit(session)
        return {'message': 'user deleted successfully!'}


class GetUserRole(Resource):
    @authorize(USER, ADMIN, SUPER_ADMIN)
    @me_or_user_id
    @json
    @swag_from('./docs/user/role.yml')
    def get(self, user_id, child_id):
        family = (
            session.query(Family)
            .filter_by(id_child=child_id)
            .filter_by(isDeleted=False)
            .first()
        )

        user = (
            session.query(UserFamily)
            .filter_by(id_user=user_id)
            .filter_by(id_family=family.id)
            .filter_by(isDeleted=False)
            .first()
        )

        return {'role': user.userRole}


class AddUser(Resource):
    @authorize(ADMIN, SUPER_ADMIN)
    @json
    @swag_from('./docs/user/add.yml')
    def post(self):

        if 'emailAddress' in request.form.keys():
            email_address = request.form['emailAddress']
        else:
            email_address = None

        if 'gender' in request.form.keys():
            gender = request.form['gender']
        else:
            gender = None

        if 'birthDate' in request.form.keys():
            birth_date = datetime.strptime(request.form['birthDate'], '%Y-%m-%d')
        else:
            birth_date = None

        if 'birthPlace' in request.form.keys():
            birth_place = int(request.form['birthPlace'])
        else:
            birth_place = None

        if 'phoneNumber' in request.form.keys():
            phone_number = request.form['phoneNumber']
        else:
            phone_number = None

        password = request.form['password']
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        city = int(request.form['city'])
        country_code = request.form['country_code']

        username = request.form['userName']

        duplicate_user = (
            session.query(User)
            .filter_by(isDeleted=False)
            .filter_by(userName=username)
            .first()
        )
        if duplicate_user is not None:
            return {'message': 'user has already been registered!'}, 400

        last_login = datetime.utcnow()

        avatar_url = 'wrong url'

        new_user = User(
            firstName=first_name,
            lastName=last_name,
            userName=username,
            avatarUrl=avatar_url,
            phoneNumber=phone_number,
            emailAddress=email_address,
            gender=gender,
            city=city,
            country_code=country_code,
            birthDate=birth_date,
            birthPlace=birth_place,
            lastLogin=last_login,
            password=password,
        )

        session.add(new_user)
        session.flush()

        if 'avatarUrl' in request.files:
            file = request.files['avatarUrl']

            if file.filename == '':
                return {'message': 'ERROR OCCURRED --> EMPTY FILE!'}, 400

            if file and allowed_image(file.filename):
                filename = str(phone_number) + '.' + file.filename.split('.')[-1]
                temp_user_path = os.path.join(
                    configs.UPLOAD_FOLDER,
                    str(new_user.id) + '-user'
                )

                if not os.path.isdir(temp_user_path):
                    os.makedirs(temp_user_path, exist_ok=True)

                path = os.path.join(
                    temp_user_path,
                    f'{randint(1000, 100000)}-avatar_{filename}'
                )

                file.save(path)

            avatar_url = path
        else:
            avatar_url = None

        new_user.avatarUrl = avatar_url
        safe_commit(session)
        return new_user


class SearchUserAPI(Resource):
    @authorize
    @json
    @swag_from('./docs/user/search.yml')
    def get(self):
        query = request.args.get('q')
        result = session.query(User.userName, User.avatarUrl) \
            .filter(func.similarity(User.userName, query) > 0.05) \
            .order_by(func.similarity(User.userName, query).desc()) \
            .limit(5) \
            .all()
       
        return [
            UserSearchSchema(user_name=r.userName, avatar_url=r.avatarUrl)
            for r in result
        ]


api.add_resource(GetUserById, '/api/v2/user/userId=<user_id>')
api.add_resource(GetUserChildren, '/api/v2/user/children/userId=<user_id>')
api.add_resource(UpdateUserById, '/api/v2/user/update/userId=<user_id>')
api.add_resource(DeleteUserById, '/api/v2/user/delete/userId=<user_id>')
api.add_resource(AddUser, '/api/v2/user/add')
api.add_resource(GetUserRole, '/api/v2/user/role/userId=<user_id>&childId=<child_id>')
api.add_resource(SearchUserAPI, '/api/v2/user/search')
