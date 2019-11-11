from hashlib import md5

from say.api.child_api import get_child_by_id, get_child_need
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
            children[str(f.family.id_child)] = get_child_by_id(session, f.family.id_child)

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
    @swag_from("./docs/user/by_id.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            resp = make_response(jsonify(get_user_by_id(session, user_id)), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserByFullName(Resource):
    @swag_from("./docs/user/by_fullname.yml")
    def get(self, first_name, last_name):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            users = (
                session.query(UserModel)
                .filter_by(firstName=first_name)
                .filter_by(lastName=last_name)
                .filter_by(isDeleted=False)
                .all()
            )

            res = {}
            for user in users:
                res[str(user.id)] = get_user_by_id(session, user.id)

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserByBirthPlace(Resource):
    @swag_from("./docs/user/by_birthplace.yml")
    def get(self, birth_place):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            users = (
                session.query(UserModel)
                .filter_by(birthPlace=birth_place)
                .filter_by(isDeleted=False)
                .all()
            )

            res = {}
            for user in users:
                res[str(user.id)] = get_user_by_id(session, user.id)

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserByBirthDate(Resource):
    @swag_from("./docs/user/by_birth_date.yml")
    def get(self, birth_date, is_after):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            if is_after.lower() == "true":
                users = (
                    session.query(UserModel)
                    .filter(UserModel.birthDate >= birth_date)
                    .filter_by(isDeleted=False)
                    .all()
                )
            else:
                users = (
                    session.query(UserModel)
                    .filter(UserModel.birthDate <= birth_date)
                    .filter_by(isDeleted=False)
                    .all()
                )

            res = {}
            for user in users:
                res[str(user.id)] = get_user_by_id(session, user.id)

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserByCountry(Resource):
    @swag_from("./docs/user/by_country.yml")
    def get(self, country):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            users = (
                session.query(UserModel)
                .filter_by(country=country)
                .filter_by(isDeleted=False)
                .all()
            )

            res = {}
            for user in users:
                res[str(user.id)] = get_user_by_id(session, user.id)

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserByCity(Resource):
    @swag_from("./docs/user/by_city.yml")
    def get(self, city):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            users = (
                session.query(UserModel)
                .filter_by(city=city)
                .filter_by(isDeleted=False)
                .all()
            )

            res = {}
            for user in users:
                res[str(user.id)] = get_user_by_id(session, user.id)

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserByUserName(Resource):
    @swag_from("./docs/user/by_username.yml")
    def get(self, username):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(UserModel).filter_by(userName=username).first()

            if not user.isDeleted:
                resp = make_response(jsonify(get_user_by_id(session, user.id)), 200)
            else:
                return make_response(jsonify({"message": "error occurred!"}), 500)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserByPhoneNumber(Resource):
    @swag_from("./docs/user/by_phone.yml")
    def get(self, phone):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(UserModel).filter_by(phoneNumber=phone).first()

            if not user.isDeleted:
                resp = make_response(jsonify(get_user_by_id(session, user.id)), 200)
            else:
                return make_response(jsonify({"message": "error occurred!"}), 500)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetAllUsers(Resource):
    @swag_from("./docs/user/all.yml")
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            users = session.query(UserModel).filter_by(isDeleted=False).all()

            user_data = {}
            for user in users:
                user_data[str(user.id)] = get_user_by_id(session, user.id)

            resp = make_response(jsonify(user_data), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserAvatar(Resource):
    @swag_from("./docs/user/avatar.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = make_response(jsonify({"avatarUrl": user.avatarUrl}), 200)
            else:
                resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserEmailAddress(Resource):
    @swag_from("./docs/user/email.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = make_response(jsonify({"emailAddress": user.emailAddress}), 200)
            else:
                resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserPhoneNumber(Resource):
    @swag_from("./docs/user/phone.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = make_response(jsonify({"phoneNumber": user.phoneNumber}), 200)
            else:
                resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserUserName(Resource):
    @swag_from("./docs/user/username.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = make_response(jsonify({"userName": user.userName}), 200)
            else:
                resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserFullName(Resource):
    @swag_from("./docs/user/fullname.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = make_response(jsonify({"firstName": user.firstName, "lastName": user.lastName}), 200)
            else:
                resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserCredit(Resource):
    @swag_from("./docs/user/credit.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = make_response(jsonify({"credit": user.credit}), 200)
            else:
                resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserRole(Resource):
    @swag_from("./docs/user/role.yml")
    def get(self, user_id, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()
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


class GetUserSpentCredit(Resource):
    @swag_from("./docs/user/spent.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = make_response(jsonify({"spentCredit": user.spentCredit}), 200)
            else:
                resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserChildren(Resource):
    @swag_from("./docs/user/children.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
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
    @swag_from("./docs/user/children-count.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
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


class GetUserNeeds(Resource):
    @swag_from("./docs/user/needs.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = make_response(jsonify(get_user_needs(session, user)), 200)
            else:
                resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserUrgentNeeds(Resource):
    @swag_from("./docs/user/urgent.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = make_response(jsonify(get_user_needs(session, user, True)), 200)
            else:
                resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetUserFinancialReport(Resource):
    @swag_from("./docs/user/report.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            payments = session.query(PaymentModel).filter_by(id_user=user_id).all()

            res = {}
            for payment in payments:
                res[str(payment.id)] = obj_to_dict(payment)

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetAllUsersNeeds(Resource):
    @swag_from("./docs/user/all_needs.yml")
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            users = session.query(UserModel).filter_by(isDeleted=False).all()

            user_needs = {}
            for user in users:
                user_needs[str(user.id)] = get_user_needs(session, user)

            resp = make_response(jsonify(user_needs), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class UpdateUserById(Resource):
    @swag_from("./docs/user/update.yml")
    def patch(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
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
                    filename = str(primary_user.phoneNumber) + '.' + file.filename.split('.')[-1]

                    temp_user_path = os.path.join(app.config['UPLOAD_FOLDER'], str(primary_user.id) + '-user')

                    for obj in os.listdir(temp_user_path):
                        check = str(primary_user.id) + '-avatar'
                        if obj.split('_')[0] == check:
                            os.remove(os.path.join(temp_user_path, obj))

                    primary_user.avatarUrl = os.path.join(temp_user_path, str(primary_user.id) + '-avatar_' + filename)

                    file.save(primary_user.avatarUrl)

            if "userName" in request.form.keys():
                primary_user.userName = request.form["userName"]

            if "emailAddress" in request.form.keys():
                primary_user.emailAddress = request.form["emailAddress"]

            if "password" in request.form.keys():
                primary_user.password = md5(
                    request.form["password"].encode()
                ).hexdigest()

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
    @swag_from("./docs/user/delete.yml")
    def patch(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
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


class AddUser(Resource):
    @swag_from("./docs/user/add.yml")
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            # if len(session.query(UserModel).all()):
            #     last_user = session.query(UserModel).order_by(UserModel.id.desc()).first()
            #     current_id = last_user.id + 1

            # else:
            #     current_id = 1

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

            phone_number = request.form['phoneNumber']
            password = md5(request.form["password"].encode()).hexdigest()
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
                # credit=11000  # TODO: remove it!
            )

            session.add(new_user)
            session.flush()

            # path = None
            if 'avatarUrl' in request.files:
                file = request.files['avatarUrl']

                if file.filename == '':
                    resp = make_response(jsonify({'message': 'ERROR OCCURRED --> EMPTY FILE!'}), 500)
                    session.close()
                    return resp

                if file and allowed_image(file.filename):
                    # filename = secure_filename(file.filename)
                    filename = str(phone_number) + '.' + file.filename.split('.')[-1]

                    temp_user_path = os.path.join(app.config['UPLOAD_FOLDER'], str(current_id) + '-user')

                    if not os.path.isdir(temp_user_path):
                        os.mkdir(temp_user_path)

                    path = os.path.join(temp_user_path, str(current_id) + '-avatar_' + filename)

                    file.save(path)

                avatar_url = path
            #     avatar_url = request.files["avatarUrl"]
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


# class Foo(Resource):
#     def get(self):
#         session_maker = sessionmaker(db)
#         session = session_maker()
#         resp = make_response(jsonify({"message": "major error occurred!"}), 503)

#         try:
#             children = (
#                 session.query(ChildModel)
#                 .filter_by(isDeleted=False)
#                 .filter_by(isMigrated=False)
#                 .filter_by(isConfirmed=True)
#                 .all()
#             )
#             users = (
#                 session.query(UserModel)
#                 .filter_by(isDeleted=False)
#                 .all()
#             )
#             for c in children:
#                 ids = []
#                 child = get_child_by_id(session, c.id, with_need=True)
#                 pay = 0

#                 for n in child["Needs"].keys():
#                     if str(child["Needs"][n]["isDone"]).lower() == 'true':
#                         c.doneNeedCount += 1

#                     ids.append(n)

#                 payments = (
#                     session.query(PaymentModel)
#                     .filter(PaymentModel.id_need.in_(ids))
#                     .filter_by(is_verified=True)
#                 )

#                 for p in payments:
#                     pay += p.amount

#                 c.spentCredit = pay

#             for u in users:
#                 payments = (
#                     session.query(PaymentModel)
#                     .filter_by(id_user=u.id)
#                 )
#                 for p in payments:
#                     u.spentCredit += p.amount

#             tag = (
#                 session.query(NeedFamilyModel)
#                 .filter_by(id_need=6)
#                 .filter_by(isDeleted=True)
#                 .first()
#             )
#             if tag is not None:
#                 tag.isDeleted = False

#             session.commit()

#             resp = make_response(dict(message="children done need counts and user spent credit fixed"), 200)

#         except Exception as e:
#             print(e)
#             resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

#         finally:
#             session.close()
#             return resp


"""
API URLs
"""

# api.add_resource(Foo, "/api/v2/foo")
api.add_resource(GetUserById, "/api/v2/user/userId=<user_id>")
api.add_resource(GetUserByFullName, "/api/v2/user/name=<first_name>&<last_name>")
api.add_resource(GetUserByBirthPlace, "/api/v2/user/birthPlace=<birth_place>")
api.add_resource(
    GetUserByBirthDate, "/api/v2/user/birthDate=<birth_date>&isAfter=<is_after>"
)
api.add_resource(GetUserByCountry, "/api/v2/user/country=<country>")
api.add_resource(GetUserByCity, "/api/v2/user/city=<city>")
api.add_resource(GetUserByUserName, "/api/v2/user/username=<username>")
api.add_resource(GetUserByPhoneNumber, "/api/v2/user/phone=<phone>")
api.add_resource(GetAllUsers, "/api/v2/user/all")
api.add_resource(GetUserAvatar, "/api/v2/user/avatar/userId=<user_id>")
api.add_resource(GetUserEmailAddress, "/api/v2/user/email/userId=<user_id>")
api.add_resource(GetUserPhoneNumber, "/api/v2/user/phone/userId=<user_id>")
api.add_resource(GetUserUserName, "/api/v2/user/username/userId=<user_id>")
api.add_resource(GetUserFullName, "/api/v2/user/fullName/userId=<user_id>")
api.add_resource(GetUserCredit, "/api/v2/user/credit/userId=<user_id>")
api.add_resource(GetUserRole, "/api/v2/user/role/userId=<user_id>&childId=<child_id>")
api.add_resource(GetUserSpentCredit, "/api/v2/user/credit/spent/userId=<user_id>")
api.add_resource(GetUserChildren, "/api/v2/user/children/userId=<user_id>")
api.add_resource(GetUserChildrenCount, "/api/v2/user/children/count/userId=<user_id>")
api.add_resource(GetUserNeeds, "/api/v2/user/needs/userId=<user_id>")
api.add_resource(GetUserFinancialReport, "/api/v2/user/report/userId=<user_id>")
api.add_resource(GetAllUsersNeeds, "/api/v2/user/needs/all")
api.add_resource(UpdateUserById, "/api/v2/user/update/userId=<user_id>")
api.add_resource(DeleteUserById, "/api/v2/user/delete/userId=<user_id>")
api.add_resource(GetUserUrgentNeeds, "/api/v2/user/needs/urgent/userId=<user_id>")
api.add_resource(AddUser, "/api/v2/user/add")
