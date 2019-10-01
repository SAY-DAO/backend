from say.models.family_model import FamilyModel
from say.models.user_family_model import UserFamilyModel
from . import *

"""
Family APIs
"""


class GetFamilyById(Resource):
    @swag_from("./docs/family/get.yml")
    def get(self, family_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            family = (
                session.query(FamilyModel)
                .filter_by(id=family_id)
                .filter_by(isDeleted=False)
                .first()
            )
            members = (
                session.query(UserFamilyModel)
                .filter_by(id_family=family_id)
                .filter_by(isDeleted=False)
                .all()
            )

            family_data, members_data = {}, {}
            for member in members:
                family_data_temp = {
                    "UserId": member.id_user,
                    "UserRole": member.userRole,
                }
                members_data[str(member.id_user)] = family_data_temp

            family_data["Members"] = members_data
            family_data["ChildId"] = family.id_child
            family_data["FamilyId"] = family.id

            resp = Response(utf8_response(family_data))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({"message": "ERROR OCCURRED"}))

        finally:
            session.close()
            return resp


class GetAllFamilies(Resource):
    @swag_from("./docs/family/all.yml")
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            families = session.query(FamilyModel).filter_by(isDeleted=False).all()

            res = {}
            for family in families:
                members = (
                    session.query(UserFamilyModel)
                    .filter_by(id_family=family.id)
                    .filter_by(isDeleted=False)
                    .all()
                )

                family_data, members_data = {}, {}
                for member in members:
                    family_data_temp = {
                        "UserId": member.id_user,
                        "UserRole": member.userRole,
                    }
                    members_data[str(member.id_user)] = family_data_temp

                family_data["Members"] = members_data
                family_data["ChildId"] = family.id_child
                family_data["FamilyId"] = family.id
                res[str(family.id)] = family_data

            resp = Response(utf8_response(res))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({"message": "ERROR OCCURRED"}))

        finally:
            session.close()
            return resp


class AddUserToFamily(Resource):
    @swag_from("./docs/family/add.yml")
    def post(self, user_id, family_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            id_user = user_id
            id_family = family_id
            # user_role = int(request.json['user_role'])
            user_role = int(request.json["userRole"])

            new_member = UserFamilyModel(
                id_user=id_user, id_family=id_family, userRole=user_role
            )

            child = (
                session.query(FamilyModel)
                .filter_by(id=id_family)
                .filter_by(isDeleted=False)
                .first()
            )
            child.family_child_relation.sayFamilyCount += 1

            session.add(new_member)
            session.commit()

            resp = Response(json.dumps({"msg": "user added to family successfully!"}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "ERROR OCCURRED!"}))

        finally:
            session.close()
            return resp


"""
API URLs 
"""

api.add_resource(GetFamilyById, "/api/v2/family/familyId=<family_id>")
api.add_resource(
    AddUserToFamily, "/api/v2/family/add/userId=<user_id>&familyId=<family_id>"
)
api.add_resource(GetAllFamilies, "/api/v2/family/all")
