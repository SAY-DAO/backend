from flasgger import swag_from
from flask import request
from flask_restful import Resource

from say.models import Family
from say.models import Invitation
from say.models import NeedFamily
from say.models import User
from say.models import UserFamily
from say.models import commit
from say.orm import safe_commit
from say.orm import session
from say.validations import VALID_ROLES

from ..authorization import authorize
from ..authorization import get_user_id
from ..config import configs
from ..decorators import json
from ..models.invite.invitation_accept import InvitationAccept
from ..roles import ADMIN
from ..roles import SAY_SUPERVISOR
from ..roles import SUPER_ADMIN
from .ext import api


'''
Family APIs
'''


class GetFamilyById(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)
    @json
    @swag_from('./docs/family/get.yml')
    def get(self, family_id):
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
                'UserId': member.id_user,
                'UserRole': member.userRole,
            }
            members_data[str(member.id_user)] = family_data_temp

        family_data['Members'] = members_data
        family_data['ChildId'] = family.id_child
        family_data['FamilyId'] = family.id

        return family_data


class GetAllFamilies(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)
    @json
    @swag_from('./docs/family/all.yml')
    def get(self):
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
                    'UserId': member.id_user,
                    'UserRole': member.userRole,
                }
                members_data[str(member.id_user)] = family_data_temp

            family_data['Members'] = members_data
            family_data['ChildId'] = family.id_child
            family_data['FamilyId'] = family.id
            res[str(family.id)] = family_data

        return res


class AddUserToFamily(Resource):

    @commit
    @json
    @authorize
    @swag_from('./docs/family/add.yml')
    def post(self):
        user_id = get_user_id()

        token = request.form.get('invitationToken', None)

        if not token:
            return {'message': 'invitationToken is required'}, 740

        invitation = session.query(Invitation) \
            .filter(Invitation.token==token) \
            .one_or_none()

        if not invitation:
            return {'message': 'Inviation not found'}, 741

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
                    user.send_installion_notif(configs.ADD_TO_HOME_URL)

            new_member = UserFamily(
                user=user,
                family=family,
                userRole=user_role,
            )
            session.add(new_member)

        else:
            if user_family.userRole != user_role:
                return {
                    f'message':
                        f'You must back to your previous role: '
                        f'{user_family.userRole}'
                }, 746

            user_family.isDeleted = False
            participations = session.query(NeedFamily) \
                .filter(NeedFamily.id_user == user.id) \
                .filter(NeedFamily.id_family == family.id)

            for p in participations:
                p.isDeleted = False

        family.child.sayFamilyCount += 1

        invitation_accept = InvitationAccept(
            invitation=invitation,
            invitee=user,
            role=user_role,
        )
        invitation.accepts.append(invitation_accept)
        return family


class LeaveFamily(Resource):

    @authorize
    @json
    @swag_from('./docs/family/leave.yml')
    def patch(self, family_id):
        user_id = get_user_id()

        family = (
            session.query(Family)
            .filter_by(id=family_id)
            .filter_by(isDeleted=False)
            .one_or_none()
        )

        if family is None:
            return {'message': 'Family not found'}, 404

        user_family = (
            session.query(UserFamily)
            .filter_by(id_user=user_id)
            .filter_by(id_family=family_id)
            .filter_by(isDeleted=False)
            .with_for_update()
            .one_or_none()
        )

        if user_family is None:
            return {'message': 'User not in family'}, 400

        user_family.isDeleted = True

        participations = (
            session.query(NeedFamily)
            .filter_by(id_user=user_id)
            .filter_by(id_family=family_id)
            .filter_by(isDeleted=False)
            .with_for_update()
        )

        for p in participations:
            p.isDeleted = True

        family.child.sayFamilyCount -= 1

        safe_commit(session)

        return {'message': 'DELETED SUCCESSFULLY!'}


api.add_resource(GetFamilyById, '/api/v2/family/familyId=<family_id>')
api.add_resource(
    AddUserToFamily, '/api/v2/family/add'
)
api.add_resource(GetAllFamilies, '/api/v2/family/all')
api.add_resource(
    LeaveFamily,
    '/api/v2/family/<family_id>/leave',
)
