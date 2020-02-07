from hashlib import md5

from say.api.child_api import get_child_by_id, get_child_need
from say.models import session, obj_to_dict
from say.models.family_model import FamilyModel
from say.models.need_family_model import NeedFamilyModel
from say.models.payment_model import PaymentModel
from say.models.user_family_model import UserFamilyModel
from say.models.user_model import UserModel
from say.models.child_model import ChildModel
from . import *

"""
User APIs
"""


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

def get_user_by_id(session, user_id):
    user = (
        session.query(UserModel)
        .filter_by(id=user_id)
        .filter_by(isDeleted=False)
        .first()
    )

    children = get_user_children(session, user)
    user_data = obj_to_dict(user)
    user_data["Children"] = children

    return user_data


def get_user_children(session, user):
    families = session.query(UserFamilyModel).filter_by(id_user=user.id).filter_by(isDeleted=False).all()

    children = {}
    for f in families:
        if f.family.child.isConfirmed:
            child = get_child_by_id(session, f.family.id_child)
            del child['phoneNumber']
            del child['firstName']
            del child['firstName_translations']
            del child['lastName']
            del child['lastName_translations']
            del child['nationality']
            del child['country']
            del child['city']
            del child['birthPlace']
            del child['address']
            del child['id_social_worker']
            del child['ngoName']
            del child['socialWorkerLastName']
            del child['socialWorkerFirstName']
            del child['id_ngo']

            children[str(f.family.id_child)] = child
    return children


def get_user_needs(session, user, urgent=False):
    families = (
        session.query(UserFamilyModel)
        .filter_by(id_user=user.id)
        .filter_by(isDeleted=False)
        .all()
    )

    needs = {}
    for family in families:
        child = (
            session.query(FamilyModel)
            .filter_by(id_child=family.family.id_child)
            .filter_by(isDeleted=False)
            .first()
        )

        needs[str(child.id_child)] = get_child_need(session, child.id_child, urgent=urgent)

    return needs


class GetUserById(Resource):

    @authorize(USER, ADMIN, SUPER_ADMIN)
    @me_or_user_id
    @swag_from("./docs/user/by_id.yml")
    def get(self, user_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            resp = make_response(jsonify(get_user_by_id(session, user_id)), 200)

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
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = make_response(jsonify(get_user_children(session, user)), 200)
            else:
                resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserChildrenCount(Resource):

    @authorize(USER, ADMIN, SUPER_ADMIN)
    @me_or_user_id
    @swag_from("./docs/user/children-count.yml")
    def get(self, user_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                child_count = session.query(UserFamilyModel) \
                    .filter_by(id_user=user.id) \
                    .filter_by(isDeleted=False) \
                    .count()
                resp = make_response(jsonify({'childrenCount': child_count}), 200)
            else:
                resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class UpdateUserById(Resource):
    @authorize(USER, ADMIN, SUPER_ADMIN)
    @me_or_user_id
    @swag_from("./docs/user/update.yml")
    def patch(self, user_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            primary_user = (
                session.query(UserModel)
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
                        str(primary_user.id) + '-avatar_' + filename,
                    )
                    file.save(primary_user.avatarUrl)
                    primary_user.avatarUrl = '/' + primary_user.avatarUrl


            if "userName" in request.form.keys():
                primary_user.userName = request.form["userName"]

            if "emailAddress" in request.form.keys():
                primary_user.emailAddress = request.form["emailAddress"]

            if "password" in request.form.keys():
                primary_user.password = request.form["password"]

            if "firstName" in request.form.keys():
                primary_user.firstName = request.form["firstName"]

            if "lastName" in request.form.keys():
                primary_user.lastName = request.form["lastName"]

            if "country" in request.form.keys():
                primary_user.country = int(request.form["country"])

            if "city" in request.form.keys():
                primary_user.city = int(request.form["city"])

            if "birthPlace" in request.form.keys():
                primary_user.birthPlace = int(request.form["birthPlace"])

            if "birthDate" in request.form.keys():
                primary_user.birthDate = datetime.strptime(
                    request.form["birthDate"], "%Y-%m-%d"
                )

            if "gender" in request.form.keys():
                primary_user.gender = (
                    True if request.form["gender"] == "true" else False
                )

            primary_user.lastUpdate = datetime.utcnow()

            secondary_user = obj_to_dict(primary_user)

            session.commit()
            resp = make_response(jsonify(secondary_user), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class DeleteUserById(Resource):
    @authorize(ADMIN, SUPER_ADMIN)
    @swag_from("./docs/user/delete.yml")
    def patch(self, user_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(UserModel).get(user_id)

            if user.isDeleted:
                resp = make_response(jsonify({"message": "user was already deleted!"}), 500)
                session.close()
                return resp

            families = (
                session.query(UserFamilyModel)
                .filter_by(id_user=user_id)
                .filter_by(isDeleted=False)
                .all()
            )
            needs = (
                session.query(NeedFamilyModel)
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
                session.query(FamilyModel)
                .filter_by(id_child=child_id)
                .filter_by(isDeleted=False)
                .first()
            )

            user = (
                session.query(UserFamilyModel)
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
                gender = True if request.form["gender"] == "true" else False
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
            country = int(request.form["country"])

            username = request.form["userName"]

            duplicate_user = (
                session.query(UserModel)
                .filter_by(isDeleted=False)
                .filter_by(userName=username)
                .first()
            )
            if duplicate_user is not None:
                resp = make_response(jsonify({"message": "user has already been registered!"}), 500)
                session.close()
                return resp

            created_at = datetime.utcnow()
            last_update = datetime.utcnow()
            last_login = datetime.utcnow()

            avatar_url = "wrong url"
            flag_url = os.path.join(FLAGS, str(country) + ".png")

            new_user = UserModel(
                firstName=first_name,
                lastName=last_name,
                userName=username,
                avatarUrl=avatar_url,
                phoneNumber=phone_number,
                emailAddress=email_address,
                gender=gender,
                city=city,
                country=country,
                createdAt=created_at,
                lastUpdate=last_update,
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

                    temp_user_path = os.path.join(app.config['UPLOAD_FOLDER'], str(current_id) + '-user')

                    if not os.path.isdir(temp_user_path):
                        os.makedirs(temp_user_path, exist_ok=True)

                    path = os.path.join(temp_user_path, str(current_id) + '-avatar_' + filename)

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
api.add_resource(GetUserChildrenCount, "/api/v2/user/children/count/userId=<user_id>")
api.add_resource(UpdateUserById, "/api/v2/user/update/userId=<user_id>")
api.add_resource(DeleteUserById, "/api/v2/user/delete/userId=<user_id>")
api.add_resource(AddUser, "/api/v2/user/add")
api.add_resource(GetUserRole, "/api/v2/user/role/userId=<user_id>&childId=<child_id>")

