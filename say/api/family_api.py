from say.models.family_model import FamilyModel
from say.models.user_family_model import UserFamilyModel
from . import *

"""
Family APIs
"""


class GetFamilyById(Resource):
    @swag_from('./apidocs/family/get.yml')
    def get(self, family_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            family = session.query(FamilyModel).filter_by(Id=family_id).filter_by(IsDeleted=False).first()
            members = session.query(UserFamilyModel).filter_by(Id_family=family_id).filter_by(IsDeleted=False).all()

            family_data = {}
            for member in members:
                family_data['UserId'] = member.Id_user
                family_data['UserRole'] = member.UserRole

            family_data['ChildId'] = family.Id_child
            family_data['FamilyId'] = family.Id

            resp = Response(json.dumps(family_data))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetAllFamilies(Resource):
    @swag_from('./apidocs/family/all.yml')
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            families = session.query(FamilyModel).filter_by(IsDeleted=False).all()

            res = {}
            for family in families:
                members = session.query(UserFamilyModel).filter_by(Id_family=family.Id).filter_by(IsDeleted=False).all()

                family_data = {}
                for member in members:
                    family_data['UserId'] = member.Id_user
                    family_data['UserRole'] = member.UserRole

                family_data['ChildId'] = family.Id_child
                family_data['FamilyId'] = family.Id
                res[family.Id] = family_data

            resp = Response(json.dumps(res))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class AddUserToFamily(Resource):
    @swag_from('./apidocs/family/add.yml')
    def post(self, user_id, family_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        print(-1)

        try:
            Id_user = user_id
            Id_family = family_id
            # UserRole = int(request.json['UserRole'])
            UserRole = int(request.form['UserRole'])
            print(0)

            new_member = UserFamilyModel(
                Id_user=Id_user,
                Id_family=Id_family,
                UserRole=UserRole,
            )
            print(1)

            child = session.query(FamilyModel).filter_by(Id=Id_family).filter_by(IsDeleted=False).first()
            child.family_child_relation.SayFamilyCount += 1
            child.family_child_relation.HasFamily = True
            print(2)

            session.add(new_member)
            session.commit()
            print(3)

            resp = Response(json.dumps({'msg': 'user added to family successfully!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED!'}))

        finally:
            session.close()
            return resp


"""
API URLs 
"""

api.add_resource(GetFamilyById, '/api/v2/family/familyId=<family_id>')
api.add_resource(AddUserToFamily, '/api/v2/family/add/userId=<user_id>&familyId=<family_id>')
api.add_resource(GetAllFamilies, '/api/v2/family/all')
