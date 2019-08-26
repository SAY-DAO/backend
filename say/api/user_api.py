from hashlib import md5

from say.api.child_api import get_child_by_id, get_child_need
from say.models.family_model import FamilyModel
from say.models.need_family_model import NeedFamilyModel
from say.models.payment_model import PaymentModel
from say.models.user_family_model import UserFamilyModel
from say.models.user_model import UserModel
from . import *

"""
User APIs
"""


def get_user_by_id(session, user_id):
    user = session.query(UserModel).filter_by(id=user_id).filter_by(isDeleted=False).first()

    children = get_user_children(session, user)
    user_data = utf8_response(obj_to_dict(user))
    user_data = user_data[:-1] + f', "Children": {children}' + '}'

    return user_data


def get_user_children(session, user):
    families = session.query(UserFamilyModel).filter_by(id_user=user.id).filter_by(isDeleted=False).all()

    children = '{'
    for family in families:
        child = session.query(FamilyModel).filter_by(id_child=family.family_relation.id_child).filter_by(
            isDeleted=False).first()

        if child.family_child_relation.isConfirmed:
            children += f'"{str(child.id_child)}": {get_child_by_id(session, child.id_child)}, '

    return children[:-2] + '}' if len(children) != 1 else '{}'


def get_user_needs(session, user, urgent=False):
    families = session.query(UserFamilyModel).filter_by(id_user=user.id).filter_by(isDeleted=False).all()

    needs = '{'
    for family in families:
        child = session.query(FamilyModel).filter_by(id_child=family.family_relation.id_child).filter_by(
            isDeleted=False).first()

        needs += f'"{str(child.id_child)}": {get_child_need(session, child.id_child, urgent)}, '

    return needs[:-2] + '}' if len(needs) != 1 else '{}'


class GetUserById(Resource):
    @swag_from('./docs/user/by_id.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            resp = Response(get_user_by_id(session, user_id))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserByFullName(Resource):
    @swag_from('./docs/user/by_fullname.yml')
    def get(self, first_name, last_name):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            users = session.query(UserModel).filter_by(firstName=first_name).filter_by(lastName=last_name).filter_by(
                isDeleted=False).all()

            res = '{'
            for user in users:
                user_data = get_user_by_id(session, user.id)
                res += f'"{str(user.id)}": {user_data}, '

            resp = Response(res[:-2] + '}' if len(res) != 1 else '{}')

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserByBirthPlace(Resource):
    @swag_from('./docs/user/by_birthplace.yml')
    def get(self, birth_place):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            users = session.query(UserModel).filter_by(birthPlace=birth_place).filter_by(isDeleted=False).all()

            res = '{'
            for user in users:
                user_data = get_user_by_id(session, user.id)
                res += f'"{str(user.id)}": {user_data}, '

            resp = Response(res[:-2] + '}' if len(res) != 1 else '{}')

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserByBirthDate(Resource):
    @swag_from('./docs/user/by_birth_date.yml')
    def get(self, birth_date, is_after):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            if is_after.lower() == 'true':
                users = session.query(UserModel).filter(UserModel.birthDate >= birth_date).filter_by(
                    isDeleted=False).all()
            else:
                users = session.query(UserModel).filter(UserModel.birthDate <= birth_date).filter_by(
                    isDeleted=False).all()

            res = '{'
            for user in users:
                user_data = get_user_by_id(session, user.id)
                res += f'"{str(user.id)}": {user_data}, '

            resp = Response(res[:-2] + '}' if len(res) != 1 else '{}')

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserByCountry(Resource):
    @swag_from('./docs/user/by_country.yml')
    def get(self, country):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            users = session.query(UserModel).filter_by(country=country).filter_by(isDeleted=False).all()

            res = '{'
            for user in users:
                user_data = get_user_by_id(session, user.id)
                res += f'"{str(user.id)}": {user_data}, '

            resp = Response(res[:-2] + '}' if len(res) != 1 else '{}')

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserByCity(Resource):
    @swag_from('./docs/user/by_city.yml')
    def get(self, city):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            users = session.query(UserModel).filter_by(city=city).filter_by(isDeleted=False).all()

            res = '{'
            for user in users:
                user_data = get_user_by_id(session, user.id)
                res += f'"{str(user.id)}": {user_data}, '

            resp = Response(res[:-2] + '}' if len(res) != 1 else '{}')

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserByUserName(Resource):
    @swag_from('./docs/user/by_username.yml')
    def get(self, username):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            user = session.query(UserModel).filter_by(userName=username).first()

            if not user.isDeleted:
                resp = Response(get_user_by_id(session, user.id))
            else:
                return {'msg': 'error occurred!'}

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserByPhoneNumber(Resource):
    @swag_from('./docs/user/by_phone.yml')
    def get(self, phone):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            user = session.query(UserModel).filter_by(phoneNumber=phone).first()

            if not user.isDeleted:
                resp = Response(get_user_by_id(session, user.id))
            else:
                return {'msg': 'error occurred!'}

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetAllUsers(Resource):
    @swag_from('./docs/user/all.yml')
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            users = session.query(UserModel).filter_by(isDeleted=False).all()

            user_data = '{'
            for user in users:
                user_dict = get_user_by_id(session, user.id)
                user_data += f'"{str(user.id)}": {user_dict}, '

            resp = Response(user_data[:-2] + '}' if len(user_data) != 1 else '{}')

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserAvatar(Resource):
    @swag_from('./docs/user/avatar.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = Response(utf8_response({'avatarUrl': user.avatarUrl}))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserEmailAddress(Resource):
    @swag_from('./docs/user/email.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = Response(utf8_response({'emailAddress': user.emailAddress}))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserPhoneNumber(Resource):
    @swag_from('./docs/user/phone.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = Response(utf8_response({'phoneNumber': user.phoneNumber}))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserUserName(Resource):
    @swag_from('./docs/user/username.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = Response(utf8_response({'userName': user.userName}))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserFullName(Resource):
    @swag_from('./docs/user/fullname.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                res = {'firstName': user.firstName,
                       'lastName': user.lastName}
                resp = Response(utf8_response(res))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserCredit(Resource):
    @swag_from('./docs/user/credit.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = Response(utf8_response({'credit': user.credit}))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserSpentCredit(Resource):
    @swag_from('./docs/user/spent.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = Response(utf8_response({'spentCredit': user.spentCredit}))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserChildren(Resource):
    @swag_from('./docs/user/children.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = Response(get_user_children(session, user))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserNeeds(Resource):
    @swag_from('./docs/user/needs.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = Response(get_user_needs(session, user))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserUrgentNeeds(Resource):
    @swag_from('./docs/user/urgent.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            user = session.query(UserModel).get(user_id)

            if not user.isDeleted:
                resp = Response(get_user_needs(session, user, True))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserFinancialReport(Resource):
    @swag_from('./docs/user/report.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            payments = session.query(PaymentModel).filter_by(id_user=user_id).all()

            res = '{'
            for payment in payments:
                res += f'"{str(payment.id)}": {utf8_response(obj_to_dict(payment))}, '

            resp = Response(res[:-2] + '}' if len(res) != 1 else '{}')

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetAllUsersNeeds(Resource):
    @swag_from('./docs/user/all_needs.yml')
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            users = session.query(UserModel).filter_by(isDeleted=False).all()

            user_needs = '{'
            for user in users:
                user_needs += f'"{str(user.id)}": {get_user_needs(session, user)}, '

            resp = Response(user_needs[:-2] + '}' if len(user_needs) != 1 else '{}')

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class UpdateUserById(Resource):
    @swag_from('./docs/user/update.yml')
    def patch(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            primary_user = session.query(UserModel).filter_by(id=user_id).filter_by(isDeleted=False).first()

            if 'avatarUrl' in request.files.keys():
                file = request.files['avatarUrl']
                if file.filename == '':
                    resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY FILE!'}))
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

                    resp = Response(json.dumps({'message': 'WELL DONE!'}))

            if 'userName' in request.json.keys():
                primary_user.userName = request.json['userName']

            if 'emailAddress' in request.json.keys():
                primary_user.emailAddress = request.json['emailAddress']

            if 'password' in request.json.keys():
                primary_user.password = md5(request.json['password'].encode()).hexdigest()

            if 'firstName' in request.json.keys():
                primary_user.firstName = request.json['firstName']

            if 'lastName' in request.json.keys():
                primary_user.lastName = request.json['lastName']

            if 'country' in request.json.keys():
                primary_user.country = int(request.json['country'])

            if 'city' in request.json.keys():
                primary_user.city = int(request.json['city'])

            if 'birthPlace' in request.json.keys():
                primary_user.birthPlace = int(request.json['birthPlace'])

            if 'birthDate' in request.json.keys():
                primary_user.birthDate = datetime.strptime(request.json['birthDate'], '%Y-%m-%d')

            if 'gender' in request.json.keys():
                primary_user.gender = True if request.json['gender'] == 'true' else False

            primary_user.lastUpdate = datetime.now()

            secondary_user = obj_to_dict(primary_user)

            session.commit()
            resp = Response(utf8_response(secondary_user))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'ERROR OCCURRED!'}))

        finally:
            session.close()
            return resp


class DeleteUserById(Resource):
    @swag_from('./docs/user/delete.yml')
    def patch(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            user = session.query(UserModel).get(user_id)

            if user.isDeleted:
                resp = Response(json.dumps({'msg': 'user was already deleted!'}))
                session.close()
                return resp

            families = session.query(UserFamilyModel).filter_by(id_user=user_id).filter_by(isDeleted=False).all()
            needs = session.query(NeedFamilyModel).filter_by(id_user=user_id).filter_by(isDeleted=False).all()

            for family in families:
                family.isDeleted = True

            for need in needs:
                need.isDeleted = True

            user.isDeleted = True

            session.commit()

            resp = Response(json.dumps({'msg': 'user deleted successfully!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class AddUser(Resource):
    @swag_from('./docs/user/add.yml')
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            if len(session.query(UserModel).all()):
                last_user = session.query(UserModel).order_by(UserModel.id.desc()).first()
                current_id = last_user.id + 1

            else:
                current_id = 1

            if 'emailAddress' in request.json.keys():
                email_address = request.json['emailAddress']
            else:
                email_address = None

            if 'gender' in request.json.keys():
                gender = True if request.json['gender'] == 'true' else False
            else:
                gender = None

            if 'birthDate' in request.json.keys():
                birth_date = datetime.strptime(request.json['birthDate'], '%Y-%m-%d')
            else:
                birth_date = None

            if 'birthPlace' in request.json.keys():
                birth_place = int(request.json['birthPlace'])
            else:
                birth_place = None

            if 'phoneNumber' in request.json.keys():
                phone_number = request.json['phoneNumber']
            else:
                phone_number = None

            # phone_number = request.json['phoneNumber']
            password = md5(request.json['password'].encode()).hexdigest()
            first_name = request.json['firstName']
            last_name = request.json['lastName']
            city = int(request.json['city'])
            country = int(request.json['country'])

            username = request.json['userName']

            duplicate_user = session.query(UserModel).filter_by(isDeleted=False).filter_by(userName=username).first()
            if duplicate_user is not None:
                resp = Response(json.dumps({'message': 'user has already been registered!'}))
                session.close()
                return resp

            created_at = datetime.now()
            last_update = datetime.now()
            last_login = datetime.now()

            # avatar_url = path
            flag_url = os.path.join(FLAGS, str(country) + '.png')

            path = None
            if 'avatarUrl' in request.files:
                # file = request.files['avatarUrl']
                #
                # if file.filename == '':
                #     resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY FILE!'}))
                #     session.close()
                #     return resp
                #
                # if file and allowed_image(file.filename):
                #     # filename = secure_filename(file.filename)
                #     filename = str(phone_number) + '.' + file.filename.split('.')[-1]
                #
                #     temp_user_path = os.path.join(app.config['UPLOAD_FOLDER'], str(current_id) + '-user')
                #
                #     if not os.path.isdir(temp_user_path):
                #         os.mkdir(temp_user_path)
                #
                #     path = os.path.join(temp_user_path, str(current_id) + '-avatar_' + filename)
                #
                #     file.save(path)
                #
                #     resp = Response(json.dumps({'message': 'WELL DONE!'}))
                #
                # avatar_url = path
                avatar_url = request.json['avatarUrl']
            else:
                avatar_url = None

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
            session.commit()

            resp = Response(json.dumps({'message': 'USER ADDED SUCCESSFULLY!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetUserById, '/api/v2/user/userId=<user_id>')
api.add_resource(GetUserByFullName, '/api/v2/user/name=<first_name>&<last_name>')
api.add_resource(GetUserByBirthPlace, '/api/v2/user/birthPlace=<birth_place>')
api.add_resource(GetUserByBirthDate, '/api/v2/user/birthDate=<birth_date>&isAfter=<is_after>')
api.add_resource(GetUserByCountry, '/api/v2/user/country=<country>')
api.add_resource(GetUserByCity, '/api/v2/user/city=<city>')
api.add_resource(GetUserByUserName, '/api/v2/user/username=<username>')
api.add_resource(GetUserByPhoneNumber, '/api/v2/user/phone=<phone>')
api.add_resource(GetAllUsers, '/api/v2/user/all')
api.add_resource(GetUserAvatar, '/api/v2/user/avatar/userId=<user_id>')
api.add_resource(GetUserEmailAddress, '/api/v2/user/email/userId=<user_id>')
api.add_resource(GetUserPhoneNumber, '/api/v2/user/phone/userId=<user_id>')
api.add_resource(GetUserUserName, '/api/v2/user/username/userId=<user_id>')
api.add_resource(GetUserFullName, '/api/v2/user/fullName/userId=<user_id>')
api.add_resource(GetUserCredit, '/api/v2/user/credit/userId=<user_id>')
api.add_resource(GetUserSpentCredit, '/api/v2/user/credit/spent/userId=<user_id>')
api.add_resource(GetUserChildren, '/api/v2/user/children/userId=<user_id>')
api.add_resource(GetUserNeeds, '/api/v2/user/needs/userId=<user_id>')
api.add_resource(GetUserFinancialReport, '/api/v2/user/report/userId=<user_id>')
api.add_resource(GetAllUsersNeeds, '/api/v2/user/needs/all')
api.add_resource(UpdateUserById, '/api/v2/user/update/userId=<user_id>')
api.add_resource(DeleteUserById, '/api/v2/user/delete/userId=<user_id>')
api.add_resource(GetUserUrgentNeeds, '/api/v2/user/needs/urgent/userId=<user_id>')
api.add_resource(AddUser, '/api/v2/user/add')
