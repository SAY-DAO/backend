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


class AddUserToFamily(Resource):
    @swag_from('./apidocs/family/add.yml')
    def patch(self, user_id, family_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            Id_user = user_id
            Id_family = family_id
            UserRole = int(request.json['UserRole'])

            new_member = UserFamilyModel(
                Id_user=Id_user,
                Id_family=Id_family,
                UserRole=UserRole,
            )

            child = session.query(FamilyModel).filter_by(Id=Id_family).filter_by(IsDeleted=False).first()
            child.SayFamilyCount += 1

            session.add(new_member)
            session.commit()

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
api.add_resource(AddUserToFamily, '/api/v2/family/add/userId=<user_id>')
