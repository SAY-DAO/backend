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


def get_user_by_something(session, user_id):
    user = session.query(UserModel).filter_by(Id=user_id).filter_by(IsDeleted=False).first()

    user_data = obj_to_dict(user)
    children = get_user_children(session, user)

    user_data['Children'] = children

    return user_data


def get_user_children(session, user):
    families = session.query(UserFamilyModel).filter_by(Id_user=user.Id).all()

    children = {}
    for family in families:
        child = session.query(FamilyModel).filter_by(Id_child=family.family_relation.Id_child).filter_by(IsDeleted=False).first()
        child_data = get_child_by_id(session, child.Id)
        children[child.Id] = child_data

    return children


def get_user_needs(session, user, urgent=False):
    families = session.query(UserFamilyModel).filter_by(Id_user=user.Id).all()

    needs = {}
    for family in families:
        child = session.query(FamilyModel).filter_by(Id_child=family.family_relation.Id_child).filter_by(IsDeleted=False).first()
        child_data = get_child_need(session, child.Id, urgent)
        needs[child.Id] = child_data

    return needs


class GetUserById(Resource):
    @swag_from('./apidocs/user/by_id.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            user = session.query(UserModel).get(user_id)

            user_data = obj_to_dict(user)
            children = get_user_children(session, user)

            user_data['Children'] = children

            if not user.IsDeleted:
                resp = Response(json.dumps(user_data))
            else:
                return {'msg': 'error occurred!'}

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserByFullName(Resource):
    @swag_from('./apidocs/user/by_fullname.yml')
    def get(self, first_name, last_name):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            users = session.query(UserModel).filter_by(FirstName=first_name).filter_by(LastName=last_name).filter_by(
                IsDeleted=False).all()

            res = {}
            for user in users:
                user_data = obj_to_dict(user)
                children = get_user_children(session, user)
                user_data['Children'] = children
                res[user.Id] = user_data

            resp = Response(json.dumps(res))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserByBirthPlace(Resource):
    @swag_from('./apidocs/user/by_birthplace.yml')
    def get(self, birth_place):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            users = session.query(UserModel).filter_by(BirthPlace=birth_place).filter_by(IsDeleted=False).all()

            res = {}
            for user in users:
                user_data = obj_to_dict(user)
                children = get_user_children(session, user)
                user_data['Children'] = children
                res[user.Id] = user_data

            resp = Response(json.dumps(res))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserByBirthDate(Resource):
    @swag_from('./apidocs/user/by_birthdate.yml')
    def get(self, birth_date):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            users = session.query(UserModel).filter_by(BirthDate=birth_date).filter_by(IsDeleted=False).all()

            res = {}
            for user in users:
                user_data = obj_to_dict(user)
                children = get_user_children(session, user)
                user_data['Children'] = children
                res[user.Id] = user_data

            resp = Response(json.dumps(res))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserByCountry(Resource):
    @swag_from('./apidocs/user/by_country.yml')
    def get(self, country):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            users = session.query(UserModel).filter_by(Country=country).filter_by(IsDeleted=False).all()

            res = {}
            for user in users:
                user_data = obj_to_dict(user)
                children = get_user_children(session, user)
                user_data['Children'] = children
                res[user.Id] = user_data

            resp = Response(json.dumps(res))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserByCity(Resource):
    @swag_from('./apidocs/user/by_city.yml')
    def get(self, city):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            users = session.query(UserModel).filter_by(City=city).filter_by(IsDeleted=False).all()

            res = {}
            for user in users:
                user_data = obj_to_dict(user)
                children = get_user_children(session, user)
                user_data['Children'] = children
                res[user.Id] = user_data

            resp = Response(json.dumps(res))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserByUserName(Resource):
    @swag_from('./apidocs/user/by_username.yml')
    def get(self, username):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            user = session.query(UserModel).filter_by(UserName=username).first()

            user_data = obj_to_dict(user)
            children = get_user_children(session, user)

            user_data['Children'] = children

            if not user.IsDeleted:
                resp = Response(json.dumps(user_data))
            else:
                return {'msg': 'error occurred!'}

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserByPhoneNumber(Resource):
    @swag_from('./apidocs/user/by_phone.yml')
    def get(self, phone):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            user = session.query(UserModel).filter_by(PhoneNumber=phone).first()

            user_data = obj_to_dict(user)
            children = get_user_children(session, user)

            user_data['Children'] = children

            if not user.IsDeleted:
                resp = Response(json.dumps(user_data))
            else:
                return {'msg': 'error occurred!'}

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetAllUsers(Resource):
    @swag_from('./apidocs/user/all.yml')
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            users = session.query(UserModel).filter_by(IsDeleted=False).all()

            user_data = {}
            for user in users:
                user_dict = get_user_by_something(session, user.Id)
                user_data[user.Id] = user_dict

            resp = Response(json.dumps(user_data))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserAvatar(Resource):
    @swag_from('./apidocs/user/avatar.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            user = session.query(UserModel).get(user_id)

            if not user.IsDeleted:
                resp = Response(json.dumps({'AvatarUrl': user.AvatarUrl}))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserEmailAddress(Resource):
    @swag_from('./apidocs/user/email.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            user = session.query(UserModel).get(user_id)

            if not user.IsDeleted:
                resp = Response(json.dumps({'EmailAddress': user.EmailAddress}))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserPhoneNumber(Resource):
    @swag_from('./apidocs/user/phone.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            user = session.query(UserModel).get(user_id)

            if not user.IsDeleted:
                resp = Response(json.dumps({'PhoneNumber': user.PhoneNumber}))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserUserName(Resource):
    @swag_from('./apidocs/user/username.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            user = session.query(UserModel).get(user_id)

            if not user.IsDeleted:
                resp = Response(json.dumps({'UserName': user.UserName}))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserFullName(Resource):
    @swag_from('./apidocs/user/fullname.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            user = session.query(UserModel).get(user_id)

            if not user.IsDeleted:
                resp = Response(json.dumps({'FirstName': user.FirstName,
                                            'LastName': user.LastName}))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserCredit(Resource):
    @swag_from('./apidocs/user/credit.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            user = session.query(UserModel).get(user_id)

            if not user.IsDeleted:
                resp = Response(json.dumps({'Credit': user.Credit}))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserSpentCredit(Resource):
    @swag_from('./apidocs/user/spent.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            user = session.query(UserModel).get(user_id)

            if not user.IsDeleted:
                resp = Response(json.dumps({'SpentCredit': user.SpentCredit}))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserChildren(Resource):
    @swag_from('./apidocs/user/children.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            user = session.query(UserModel).get(user_id)

            if not user.IsDeleted:
                resp = Response(json.dumps(get_user_children(session, user)))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserNeeds(Resource):
    @swag_from('./apidocs/user/needs.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            user = session.query(UserModel).get(user_id)

            if not user.IsDeleted:
                resp = Response(json.dumps(get_user_needs(session, user)))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserUrgentNeeds(Resource):
    @swag_from('./apidocs/user/urgents.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            user = session.query(UserModel).get(user_id)

            if not user.IsDeleted:
                resp = Response(json.dumps(get_user_needs(session, user, True)))
            else:
                resp = Response(json.dumps({'msg': 'error occurred!'}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetUserTokenById(Resource):
    pass


class GetUserFinancialReport(Resource):
    @swag_from('./apidocs/user/report.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            payments = session.query(PaymentModel).filter_by(Id_user=user_id).all()

            res = {}
            for payment in payments:
                res[payment.Id] = obj_to_dict(payment)

            resp = Response(json.dumps(res))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetAllUsersNeeds(Resource):
    @swag_from('./apidocs/user/all_needs.yml')
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            users = session.query(UserModel).filter_by(IsDeleted=False).all()

            user_needs = {}
            for user in users:
                need = get_user_needs(session, user)
                user_needs[user.Id] = need

            resp = Response(json.dumps(user_needs))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class UpdateUserById(Resource):
    @swag_from('./apidocs/user/update.yml')
    def patch(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            primary_user = session.query(UserModel).filter_by(Id=user_id).filter_by(IsDeleted=False).first()

            if 'AvatarUrl' in request.files.keys():
                file = request.files['AvatarUrl']
                if file.filename == '':
                    resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY FILE!'}))
                    session.close()
                    return resp
                if file and allowed_image(file.filename):
                    filename = secure_filename(file.filename)
                    temp_user_path = os.path.join(app.config['UPLOAD_FOLDER'], str(primary_user.Id) + '-user')
                    for obj in os.listdir(temp_user_path):
                        check = str(primary_user.Id) + '-avatar'
                        if obj.split('_')[0] == check:
                            os.remove(os.path.join(temp_user_path, obj))
                    primary_user.AvatarUrl = os.path.join(temp_user_path, str(primary_user.Id) + '-avatar_' + filename)
                    file.save(primary_user.AvatarUrl)
                    resp = Response(json.dumps({'message': 'WELL DONE!'}))
            if 'UserName' in request.form.keys():
                primary_user.UserName = request.form['UserName']
            if 'EmailAddress' in request.form.keys():
                primary_user.EmailAddress = request.form['EmailAddress']
            if 'Password' in request.form.keys():
                primary_user.Password = request.form['Password']
            if 'FirstName' in request.form.keys():
                primary_user.FirstName = request.form['FirstName']
            if 'LastName' in request.form.keys():
                primary_user.LastName = request.form['LastName']
            if 'Country' in request.form.keys():
                primary_user.Country = int(request.form['Country'])
            if 'City' in request.form.keys():
                primary_user.City = int(request.form['City'])
            if 'BirthPlace' in request.form.keys():
                primary_user.BirthPlace = request.form['BirthPlace']
            if 'BirthDate' in request.form.keys():
                primary_user.BirthDate = datetime.strptime(request.form['BirthDate'], '%Y-%m-%d')
            if 'Gender' in request.form.keys():
                primary_user.Gender = True if request.form['Gender'] == 'true' else False

            primary_user.LastUpdate = datetime.now()

            secondary_user = obj_to_dict(primary_user)

            session.commit()
            resp = Response(json.dumps(secondary_user))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'ERROR OCCURRED!'}))

        finally:
            session.close()
            return resp


class DeleteUserById(Resource):
    @swag_from('./apidocs/user/delete.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            user = session.query(UserModel).get(user_id)

            if user.IsDeleted:
                resp = Response(json.dumps({'msg': 'user was already deleted!'}))
                session.close()
                return resp

            families = session.query(UserFamilyModel).filter_by(Id_user=user_id).filter_by(IsDeleted=False).all()
            needs = session.query(NeedFamilyModel).filter_by(Id_user=user_id).filter_by(IsDeleted=False).all()

            for family in families:
                family.IsDeleted = True

            for need in needs:
                need.IsDeleted = True

            user.IsDeleted = True

            session.commit()

            resp = Response(json.dumps({'msg': 'user deleted successfully!'}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class AddUser(Resource):
    @swag_from('./apidocs/user/add.yml')
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            if len(session.query(UserModel).all()):
                last_user = session.query(UserModel).order_by(UserModel.Id.desc()).first()
                current_id = last_user.Id + 1
            else:
                current_id = 1

            path = None
            if 'AvatarUrl' in request.files:
                file = request.files['AvatarUrl']
                if file.filename == '':
                    resp =  Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY FILE!'}))
                    session.close()
                    return resp
                if file and allowed_image(file.filename):
                    filename = secure_filename(file.filename)

                    temp_user_path = os.path.join(app.config['UPLOAD_FOLDER'], str(current_id) + '-user')
                    if not os.path.isdir(temp_user_path):
                        os.mkdir(temp_user_path)

                    path = os.path.join(temp_user_path, str(current_id) + '-avatar_' + filename)
                    file.save(path)
                    resp = Response(json.dumps({'message': 'WELL DONE!'}))

            PhoneNumber = request.form['PhoneNumber']
            if 'EmailAddress' in request.form.keys():
                EmailAddress = request.form['EmailAddress']
            else:
                EmailAddress = None
            if 'Gender' in request.form.keys():
                Gender = True if request.form['Gender'] == 'true' else False
            else:
                Gender = None
            if 'BirthDate' in request.form.keys():
                BirthDate = datetime.strptime(request.form['BirthDate'], '%Y-%m-%d')
            else:
                BirthDate = None
            if 'BirthPlace' in request.form.keys():
                BirthPlace = request.form['BirthPlace']
            else:
                BirthPlace = None
            LastLogin = datetime.now()
            Password = request.form['Password']
            FirstName = request.form['FirstName']
            LastName = request.form['LastName']
            UserName = request.form['UserName']
            AvatarUrl = path
            City = int(request.form['City'])
            Country = int(request.form['Country'])
            CreatedAt = datetime.now()
            LastUpdate = datetime.now()
            FlagUrl = os.path.join(FLAGS, str(Country) + '.png')

            new_user = UserModel(
                FirstName=FirstName,
                LastName=LastName,
                UserName=UserName,
                AvatarUrl=AvatarUrl,
                PhoneNumber=PhoneNumber,
                EmailAddress=EmailAddress,
                Gender=Gender,
                City=City,
                Country=Country,
                CreatedAt=CreatedAt,
                LastUpdate=LastUpdate,
                BirthDate=BirthDate,
                BirthPlace=BirthPlace,
                LastLogin=LastLogin,
                Password=Password,
                FlagUrl=FlagUrl
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
api.add_resource(GetUserByBirthDate, '/api/v2/user/birthDate=<birth_date>')
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
api.add_resource(GetUserTokenById, '/api/v2/user/token/userId=<user_id>')
api.add_resource(GetUserFinancialReport, '/api/v2/user/report/userId=<user_id>')
api.add_resource(GetAllUsersNeeds, '/api/v2/user/needs/all')
api.add_resource(UpdateUserById, '/api/v2/user/update/userId=<user_id>')
api.add_resource(DeleteUserById, '/api/v2/user/delete/userId=<user_id>')
api.add_resource(GetUserUrgentNeeds, '/api/v2/user/needs/urgent/userId=<user_id>')
api.add_resource(AddUser, '/api/v2/user/add')
