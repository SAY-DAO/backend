from flasgger import swag_from
from flask import request
from flask_restful import Resource

from say.crud.family import join_family
from say.exceptions import HTTPException
from say.models import Family
from say.models import Invitation
from say.models import NeedFamily
from say.models import User
from say.models import UserFamily
from say.models import commit
from say.orm import safe_commit
from say.orm import session
from say.schema.family import JoinFamilySchema

from ..authorization import authorize
from ..authorization import get_user_id
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
    @authorize
    @commit
    @json
    @swag_from('./docs/family/add.yml')
    def post(self):
        user_id = get_user_id()

        token = request.form.get('invitationToken', None)

        if not token:
            return {'message': 'invitationToken is required'}, 740

        invitation = (
            session.query(Invitation).filter(Invitation.token == token).one_or_none()
        )

        if not invitation:
            return {'message': 'Inviation not found'}, 741

        id_family = invitation.family_id
        user_role = invitation.role

        user = session.query(User).with_for_update().get(user_id)
        if not user or user.isDeleted:
            raise HTTPException(745, 'User not found')

        family = join_family(id_family, user_role, user)
        invitation_accept = InvitationAccept(
            invitation=invitation,
            invitee=user,
            role=user_role,
        )
        invitation.accepts.append(invitation_accept)
        return family


class JoinFamilyV3(Resource):
    @authorize
    @commit
    @json
    @swag_from('./docs/family/join-v3.yml')
    def post(self, family_id):

        try:
            data = JoinFamilySchema(
                **request.form.to_dict(),
                family_id=family_id,
            )
        except ValueError as ex:
            return ex.json(), 400

        user_id = get_user_id()
        id_family = data.family_id
        user_role = data.role

        user = session.query(User).with_for_update().get(user_id)
        if not user or user.isDeleted:
            raise HTTPException(745, 'User not found')

        family = join_family(id_family, user_role, user)
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
api.add_resource(AddUserToFamily, '/api/v2/family/add')
api.add_resource(JoinFamilyV3, '/api/v3/families/<family_id>/join')
api.add_resource(GetAllFamilies, '/api/v2/family/all')
api.add_resource(
    LeaveFamily,
    '/api/v2/family/<family_id>/leave',
)
