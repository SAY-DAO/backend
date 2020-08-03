from builtins import int
from datetime import datetime

from flasgger import swag_from
from flask import request
from flask_restful import Resource

from say.api import api, app
from say.authorization import authorize, get_user_id
from say.decorators import json
from say.models import commit, session, Invitation, InvitationStatus, \
    UserFamily, User, NeedFamily, Family, Child
from say.orm import obj_to_dict


class AcceptInvitationAPI(Resource):

    @json
    @commit
    @authorize
    @swag_from("../docs/invitation/accept.yml")
    def post(self, token: str):
        user_id = get_user_id()

        invitation = session.query(Invitation) \
            .filter(Invitation.token == token) \
            .filter(Invitation.invitee_id == user_id) \
            .filter(Invitation.status == InvitationStatus.pending.value) \
            .one_or_none()

        # Check for indirect invitation
        if not invitation:
            invitation = session.query(Invitation) \
                .filter(Invitation.token == token) \
                .filter(Invitation.invitee_id.is_(None)) \
                .filter(Invitation.status == InvitationStatus.pending.value) \
                .one_or_none()

            if not invitation:
                return {'message': 'Invitation not found'}, 404

            # create a direct invitation from indirect one
            indirect_invite = obj_to_dict(invitation)

            # remove pk
            del indirect_invite['id']

            indirect_invite.update(dict(
                invitee_id=user_id,
            ))
            invitation = Invitation(**indirect_invite)
            session.add(invitation)

        user_family = (
            session.query(UserFamily)
            .filter_by(id_user=user_id)
            .filter_by(id_family=invitation.family_id)
            .with_for_update()
            .first()
        )

        if not user_family:
            user = session.query(User).get(user_id)
            if not user.is_installed:
                family_count = session.query(UserFamily.id) \
                    .filter(UserFamily.id_user == user_id) \
                    .count()

                if family_count == 0:
                    user.send_installion_notif(app.config['ADD_TO_HOME_URL'])

            new_member = UserFamily(
                user=user,
                id_family=invitation.family_id,
                userRole=invitation.role,
            )
            session.add(new_member)

        elif user_family.isDeleted is False:
            return {'message': 'already in family'}, 747

        else:
            user_family.isDeleted = False

            participators = session.query(NeedFamily) \
                .filter(NeedFamily.id_user == user_id) \
                .filter(NeedFamily.id_family == invitation.family_id)

            for p in participators:
                p.isDeleted = False

        session.query(Family) \
            .filter(Family.id == invitation.family_id) \
            .update({'say_family_count': Family.say_family_count + 1})

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

        # Reject other father or mother invites
        if invitation.role in (0, 1):
            session.query(Invitation) \
                .filter(Invitation.id != invitation.id) \
                .filter(Invitation.family_id == invitation.family_id) \
                .filter(Invitation.status == InvitationStatus.pending.value) \
                .filter(Invitation.role == invitation.role) \
                .update({
                    'status': InvitationStatus.rejected.value,
                    'reject_reason': 'Madjeed, you say!',
                    'rejected_at': datetime.utcnow(),
                })

        invitation.accept()
        return invitation


api.add_resource(AcceptInvitationAPI, '/api/v2/invitations/<token>/accept')

