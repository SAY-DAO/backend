from say.validations import VALID_ROLES
from say.models import session, obj_to_dict, commit, InvitationStatus
from say.models import User, Family, UserFamily, NeedFamily, Invitation
from . import *
from .. import crud
from ..crud.user_family import UserAlreadyInFamily, NoAvailableRole
from ..schema.family import AvailableRolesSchema

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
    @json
    @authorize
    @swag_from("./docs/family/add.yml")
    def post(self):
        user_id = get_user_id()

        token = request.form.get('invitationToken', None)

        if not token:
            return {'message': 'invitationToken is required'}, 740

        invitation = session.query(Invitation) \
            .filter(Invitation.token == token) \
            .one_or_none()

        if not invitation:
            return {'message': 'Invitation not found'}, 741

        id_family = invitation.family_id
        user_role = invitation.role

        if user_role not in VALID_ROLES:
            return {'message': 'Invalid Role'}, 742

        user = session.query(User).with_for_update().get(user_id)
        if not user or user.isDeleted:
            return {'message': 'User not found'}, 745

        family = session.query(Family).with_for_update().get(id_family)

        if not family or family.child.isDeleted:
            return {'message': f'family {id_family} not found'}, 743

        if not family.can_join(user, user_role):
            return {'message': 'Can not join this family'}, 744

        if not family.is_in_family(user):
            return {'message': 'You already joined'}, 747

        user_family = (
            session.query(UserFamily)
            .filter_by(id_user=user_id)
            .filter_by(id_family=id_family)
            .first()
        )

        if not user_family:
            if not user.is_installed:
                family_count = session.query(UserFamily) \
                    .filter(UserFamily.id_user==user_id) \
                    .count()

                if family_count == 0:
                    user.send_installion_notif(app.config['ADD_TO_HOME_URL'])

            new_member = UserFamily(
                user=user,
                family=family,
                userRole=user_role,
            )
            session.add(new_member)

        else:
            if user_family.userRole != user_role:
                return {'message':
                            f'You must back to your previous role: '
                            f'{user_family.userRole}'
                }, 746

            user_family.isDeleted = False

            participations = session.query(NeedFamily) \
                .filter(NeedFamily.id_user==user.id) \
                .filter(NeedFamily.id_family==family.id)

            for p in participations:
                p.isDeleted = False

        family.say_family_count += 1

        if invitation:
            invitation.accept()

            # Reject other invitations to this family
            session.query(Invitation) \
                .filter(Invitation.id != invitation.id) \
                .filter(Invitation.family_id == invitation.family_id) \
                .filter(Invitation.status == InvitationStatus.pending.value) \
                .filter(Invitation.invitee_id == user_id) \
                .update({
                    'status': InvitationStatus.rejected.value,
                    'reject_reason': 'Madjeed, you say!',
                    'rejected_at': datetime.utcnow(),
                })

        return family


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

            family.say_family_count -= 1

            session.commit()

            resp = make_response(jsonify({"message": "DELETED SUCCESSFULLY!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class AvailableRoles(Resource):

    @json
    @swag_from("./docs/family/available_roles.yml")
    def post(self, family_id):
        try:
            data = AvailableRolesSchema(**request.form.to_dict())
        except ValueError as ex:
            return ex.json(), 400

        user_id = get_user_id()
        if not crud.user_family.is_user_in_family(user_id=user_id):
            return HTTP_NOT_FOUND()

        roles = []

        try:
            roles = crud.user_family.available_roles(
                family_id=family_id, username=data.username,
            )
        except UserAlreadyInFamily:
            return {'message': 'user in family'}, 400
        except NoAvailableRole:
            return {'message': 'no available role'}, 400

        return list(roles)


"""
API URLs
"""

api.add_resource(GetFamilyById, "/v2/family/familyId=<family_id>")
api.add_resource(
    AddUserToFamily, "/v2/family/add"
)
api.add_resource(GetAllFamilies, "/v2/family/all")
api.add_resource(
    LeaveFamily,
    "/v2/family/<family_id>/leave",
)

api.add_resource(
    AvailableRoles,
    "/v2/family/<family_id>/available_roles",
)
