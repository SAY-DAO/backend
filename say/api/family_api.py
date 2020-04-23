from say.constants import PAST_PARTICIPANT_ROLE
from say.validations import VALID_ROLES
from say.models import session, obj_to_dict
from say.models.user_model import User
from say.models.family_model import Family
from say.models.user_family_model import UserFamily
from say.models.need_family_model import NeedFamily
from . import *

"""
Family APIs
"""


class GetFamilyById(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)
    @swag_from("./docs/family/get.yml")
    def get(self, family_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            family = (
                session.query(Family)
                .filter_by(id=family_id)
                .filter_by(isDeleted=False)
                .first()
            )
            members = (
                session.query(UserFamily)
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
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            families = session.query(Family).filter_by(isDeleted=False).all()

            res = {}
            for family in families:
                members = (
                    session.query(UserFamily)
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

    @commit
    @authorize
    @swag_from("./docs/family/add.yml")
    def post(self):
#        user_id = get_user_id()
#
#        token = request.args.get('invitationToken', None)
#
#        if not token:
#            return {'message': 'invitationToken is required'}, 740
#
#        invitation = session.query(Invitation) \
#            .filter(Invitation.token==token) \
#            .one_or_none()
#
#        if not invitation:
#            return {'message': 'Inviation not found'}, 741
#
#        id_family = invitation.family_id
#        user_role = invitation.role
#        if user_role not in VALID_ROLES:
#            return {'message': 'Invalid Role'}, 742
#
#        family = session.query(Family).with_for_update().get(id_family)
#        if not family or family.child.isDeleted:
#            return {'message': f'family {id_family} not found'}, 743
#
#        if not family.can_join(user, user_role):
#            return
#                jsonify({
#                    'message':
#                        'Can not join this family'
#                }),
#                422,
#            )
#
#        user_family = (
#            session.query(UserFamily)
#            .filter_by(id_user=user_id)
#            .filter_by(id_family=family_id)
#            .first()
#        )
#
#        if not user_family:
#            new_member = UserFamily(
#                user=user,
#                family=family,
#                userRole=user_role,
#            )
#
#        else:
#            if user_family.userRole != user_role:
#                resp = make_response(
#                    jsonify({
#                        'message':
#                            f'You must back to your previous role: '
#                            f'{user_family.userRole}'
#                    }),
#                    422
#                )
#                return
#
#            user_family.isDeleted = False
#            participations = session.query(NeedFamily) \
#                .filter(NeedFamily.id_user==user.id) \
#                .filter(NeedFamily.id_family==family.id)
#
#            for p in participations:
#                p.isDeleted = False
#
#        family.child.sayFamilyCount += 1
        return {}


class LeaveFamily(Resource):

    @authorize
    @swag_from("./docs/family/leave.yml")
    def patch(self, family_id):
        user_id = get_user_id()

        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            family = (
                session.query(Family)
                .filter_by(id=family_id)
                .filter_by(isDeleted=False)
                .first()
            )
            user_family = (
                session.query(UserFamily)
                .filter_by(id_user=user_id)
                .filter_by(id_family=family_id)
                .filter_by(isDeleted=False)
                .one()
            )
            user_family.isDeleted = True

            participations = (
                session.query(NeedFamily)
                .filter_by(id_user=user_id)
                .filter_by(id_family=family_id)
                .filter_by(isDeleted=False)
            )

            for p in participations:
                p.isDeleted = True

            family.child.sayFamilyCount -= 1

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

