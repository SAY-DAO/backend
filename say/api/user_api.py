import os
from random import randint

from . import *
from say.api import jwt
from say.gender import Gender
from say.models import session, obj_to_dict
from say.models.family_model import Family
from say.models.need_family_model import NeedFamily
from say.models.revoked_token_model import RevokedToken
from say.models.user_family_model import UserFamily
from say.models.user_model import User
from ..schema.user import UserNameSchema

"""
User APIs
"""


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']

    return RevokedToken.is_jti_blacklisted(jti, session)


def is_int(maybe_int):
    try:
        int(maybe_int)
        return True
    except:
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
            return make_response(jsonify({'message': 'Permission Denied'}), 403)

        kwargs['user_id'] = user_id
        return func(*args, **kwargs)

    return wrapper


class GetUserById(Resource):

    @authorize(USER, ADMIN, SUPER_ADMIN)
    @me_or_user_id
    @swag_from("./docs/user/by_id.yml")
    def get(self, user_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = (
                session.query(User)
                .filter_by(id=user_id)
                .filter_by(isDeleted=False)
                .first()
            )
            resp = make_response(jsonify(obj_to_dict(user)), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserChildren(Resource):

    @authorize(USER, ADMIN, SUPER_ADMIN)
    @me_or_user_id
    @swag_from("./docs/user/children.yml")
    def get(self, user_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(User).get(user_id)
            if user.isDeleted:
                resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

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
            resp = make_response(jsonify(result), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class UpdateUserById(Resource):

    @authorize(USER, ADMIN, SUPER_ADMIN)
    @me_or_user_id
    @json
    @swag_from("./docs/user/update.yml")
    def patch(self, user_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            primary_user = (
                session.query(User)
                .filter_by(id=user_id)
                .filter_by(isDeleted=False)
                .first()
            )

            if 'avatarUrl' in request.files.keys():
                # primary_user.avatarUrl = request.files['avatarUrl']
                file = request.files['avatarUrl']
                if file.filename == '':
                    resp = make_response(jsonify({'message': 'ERROR OCCURRED --> EMPTY FILE!'}), 500)
                    session.close()
                    return resp

                if file and allowed_image(file.filename):
                    # filename = secure_filename(file.filename)
                    filename = str(primary_user.id) + '.' + file.filename.split('.')[-1]

                    temp_user_path = os.path.join(
                        app.config['UPLOAD_FOLDER'],
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

            raw_username = request.form.get("userName", primary_user.userName)
            if raw_username != primary_user.userName:
                try:
                    username = UserNameSchema(username=raw_username).username
                except ValueError as ex:
                    resp = ex.json(), 400
                    return resp

                if session.query(User) \
                    .filter(User.formated_username==username.lower()) \
                    .filter(User.id!=primary_user.id) \
                    .filter(User.isDeleted==False) \
                    .one_or_none() \
                :
                    resp = make_response(
                        jsonify({"message": "Username exists"}),
                        499,
                    )
                    return resp

                primary_user.userName = username

            if "emailAddress" in request.form.keys():
                primary_user.emailAddress = request.form["emailAddress"]

            if "password" in request.form.keys():
                primary_user.password = request.form["password"]

            if "firstName" in request.form.keys():
                primary_user.firstName = request.form["firstName"]

            if "lastName" in request.form.keys():
                primary_user.lastName = request.form["lastName"]

            if "country_code" in request.form.keys():
                primary_user.country_code = request.form["country_code"]

            if "city" in request.form.keys():
                primary_user.city = int(request.form["city"])

            if "postal_address" in request.form.keys():
                primary_user.postal_address = request.form["postal_address"]

            if "postal_code" in request.form.keys():
                postal_code_temp = request.form["postal_code"]
                if is_int(postal_code_temp) and len(postal_code_temp) == 10:
                    primary_user.postal_code = postal_code_temp
                else:
                    resp = make_response(
                        jsonify({"message":
                            "Invalid postal code, it must have exactly 10 digits without dash."
                        }),
                        498,
                    )
                    return resp

            if "birthPlace" in request.form.keys():
                primary_user.birthPlace = int(request.form["birthPlace"])

            if "locale" in request.form.keys():
                primary_user.locale = request.form["locale"].lower()

            if "phoneNumber" in request.form.keys() and \
                    not primary_user.is_phonenumber_verified:
                primary_user.phone_number = request.form["phoneNumber"]

            if "birthDate" in request.form.keys():
                primary_user.birthDate = datetime.strptime(
                    request.form["birthDate"], "%Y-%m-%d"
                )

            if "gender" in request.form.keys():
                gender = request.form['gender']
                if not hasattr(Gender, gender):
                    resp = make_response(
                        jsonify({"message":
                            f"Invalid gender, only can selected in "
                            f"{Gender.__members__.keys()}"
                        }),
                        498,
                    )
                    return resp

                primary_user.gender = request.form["gender"]

            secondary_user = obj_to_dict(primary_user)

            session.commit()
            resp = make_response(jsonify(secondary_user), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": str(e)}), 500)

        finally:
            session.close()
            return resp


class DeleteUserById(Resource):
    @authorize(ADMIN, SUPER_ADMIN)
    @swag_from("./docs/user/delete.yml")
    def patch(self, user_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(User).get(user_id)

            if user.isDeleted:
                resp = make_response(jsonify({"message": "user was already deleted!"}), 500)
                session.close()
                return resp

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

            session.commit()

            resp = make_response(jsonify({"message": "user deleted successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserRole(Resource):
    @authorize(USER, ADMIN, SUPER_ADMIN)
    @me_or_user_id
    @swag_from("./docs/user/role.yml")
    def get(self, user_id, child_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
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

            resp = make_response(jsonify({"role": user.userRole}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class AddUser(Resource):
    @authorize(ADMIN, SUPER_ADMIN)
    @swag_from("./docs/user/add.yml")
    def post(self):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            if "emailAddress" in request.form.keys():
                email_address = request.form["emailAddress"]
            else:
                email_address = None

            if "gender" in request.form.keys():
                gender = request.form["gender"]
            else:
                gender = None

            if "birthDate" in request.form.keys():
                birth_date = datetime.strptime(request.form["birthDate"], "%Y-%m-%d")
            else:
                birth_date = None

            if "birthPlace" in request.form.keys():
                birth_place = int(request.form["birthPlace"])
            else:
                birth_place = None

            if "phoneNumber" in request.form.keys():
                phone_number = request.form["phoneNumber"]
            else:
                phone_number = None

            password = request.form["password"]
            first_name = request.form["firstName"]
            last_name = request.form["lastName"]
            city = int(request.form["city"])
            country_code = request.form["country_code"]

            username = request.form["userName"]

            duplicate_user = (
                session.query(User)
                .filter_by(isDeleted=False)
                .filter_by(userName=username)
                .first()
            )
            if duplicate_user is not None:
                resp = make_response(jsonify({"message": "user has already been registered!"}), 500)
                session.close()
                return resp

            last_login = datetime.utcnow()

            avatar_url = "wrong url"
            flag_url = os.path.join(FLAGS, country_code + ".png")

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
                flagUrl=flag_url,
            )

            session.add(new_user)
            session.flush()

            if 'avatarUrl' in request.files:
                file = request.files['avatarUrl']

                if file.filename == '':
                    resp = make_response(jsonify({'message': 'ERROR OCCURRED --> EMPTY FILE!'}), 500)
                    session.close()
                    return resp

                if file and allowed_image(file.filename):
                    filename = str(phone_number) + '.' + file.filename.split('.')[-1]
                    temp_user_path = os.path.join(
                        app.config['UPLOAD_FOLDER'],
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

            session.commit()

            resp = make_response(jsonify({"message": "USER ADDED SUCCESSFULLY!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp




"""
API URLs
"""

api.add_resource(GetUserById, "/api/v2/user/userId=<user_id>")
api.add_resource(GetUserChildren, "/api/v2/user/children/userId=<user_id>")
api.add_resource(UpdateUserById, "/api/v2/user/update/userId=<user_id>")
api.add_resource(DeleteUserById, "/api/v2/user/delete/userId=<user_id>")
api.add_resource(AddUser, "/api/v2/user/add")
api.add_resource(GetUserRole, "/api/v2/user/role/userId=<user_id>&childId=<child_id>")
