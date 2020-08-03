import flask_jwt_extended

from say import crud
from say.api import *
from say.crud import family
from say.crud.user_family import UserAlreadyInFamily, NoAvailableRole
from say.models import commit, session, Invitation
from say.models import Invitation, Family
from say.models.invite.invitations import InvitationStatus
from say.schema.invitation import NewInvitationSchema
from say.validations import VALID_ROLES


class InvitationAPI(Resource):

    decorators = [limiter.limit("10/minute")]

    @authorize
    @json
    @commit
    @swag_from('../docs/invitation/create.yml')
    def post(self):
        try:
            data = NewInvitationSchema(**request.form.to_dict())
        except ValueError as ex:
            return ex.json(), 400

        if data.role and data.role not in VALID_ROLES:
            return {'message': f'invalid role: {data.role}'}, 700

        if not crud.family.exists_by_id(data.family_id):
            return {'message': f'family {data.family_id} not exists'}, 702

        inviter_id = get_user_id()
        invitation = session.query(Invitation) \
            .filter(Invitation.family_id == data.family_id) \
            .filter(Invitation.inviter_id == inviter_id) \
            .filter(Invitation.invitee_username == data.invitee_username) \
            .filter(Invitation.role == data.role) \
            .filter(Invitation.status == InvitationStatus.pending.value) \
            .first()

        if invitation:
            return invitation

        invitee_id = None
        if invitee_username := data.invitee_username:
            if not (invitee_id := crud.user.id_by_username(invitee_username)):
                return {'message': f'user {invitee_username} not exists'}, 701

            try:
                roles = crud.user_family.available_roles(
                    family_id=data.family_id, username=data.invitee_username,
                )
                if data.role not in roles:
                    return {'message': f'Only role {roles} is valid'}, 745

            except UserAlreadyInFamily:
                return {'message': 'user in family'}, 747
            except NoAvailableRole:
                return {'message': 'no available role'}, 744

        invitation = Invitation(
            family_id=data.family_id,
            inviter_id=inviter_id,
            invitee_id=invitee_id,
            role=data.role,
        )

        session.add(invitation)
        return invitation


api.add_resource(InvitationAPI, '/api/v2/invitations')
