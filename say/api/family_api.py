from say.models.family_model import FamilyModel
from say.models.user_family_model import UserFamilyModel
from say.models.need_family_model import NeedFamilyModel
from . import *

"""
Family APIs
"""


class GetFamilyById(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)
    @swag_from("./docs/family/get.yml")
    def get(self, family_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

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

            resp = make_response(jsonify(family_data), 200)

        except Exception as e:
            print(e)

            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetAllFamilies(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)
    @swag_from("./docs/family/all.yml")
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

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

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)

            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class AddUserToFamily(Resource):
    @authorize
    @swag_from("./docs/family/add.yml")
    def post(self, family_id):
        user_id = get_user_id()
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            id_user = user_id
            id_family = family_id
            user_role = int(request.json["userRole"])

            duplicate_family = (
                session.query(UserFamilyModel)
                .filter_by(id_user=user_id)
                .filter_by(id_family=family_id)
                .filter_by(isDeleted=False)
                .first()
            )

            if duplicate_family is not None:
                resp = make_response(jsonify({"message": "You already had this child in your family!"}), 499)
                session.close()
                return resp

            new_member = UserFamilyModel(
                id_user=id_user, id_family=id_family, userRole=user_role
            )

            family = (
                session.query(FamilyModel)
                .filter_by(id=id_family)
                .filter_by(isDeleted=False)
                .first()
            )
            family.child.sayFamilyCount += 1

            session.add(new_member)
            session.commit()

            resp = make_response(jsonify({"msg": "user added to family successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED!"}), 500)

        finally:
            session.close()
            return resp


class LeaveFamily(Resource):

    @authorize
    @swag_from("./docs/family/leave.yml")
    def patch(self, family_id):
        user_id = get_user_id()

        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            family = (
                session.query(FamilyModel)
                .filter_by(id=family_id)
                .filter_by(isDeleted=False)
                .first()
            )
            user_family = (
                session.query(UserFamilyModel)
                .filter_by(id_user=user_id)
                .filter_by(id_family=family_id)
                .filter_by(isDeleted=False)
                .first()
            )
            participation = (
                session.query(NeedFamilyModel)
                .filter_by(id_user=user_id)
                .filter_by(id_family=user_id)
                .filter_by(isDeleted=False)
            )

            # TODO: WHY?
            for participate in participation:
                participate.isDeleted = True

            family.child.sayFamilyCount -= 1
            user_family.isDeleted = True

            session.commit()

            resp = make_response(jsonify({"message": "DELETED SUCCESSFULLY!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetFamilyById, "/api/v2/family/familyId=<family_id>")
api.add_resource(
    AddUserToFamily, "/api/v2/family/add/familyId=<family_id>"
)
api.add_resource(GetAllFamilies, "/api/v2/family/all")
api.add_resource(
    LeaveFamily,
    "/api/v2/family/<family_id>/leave",
)

