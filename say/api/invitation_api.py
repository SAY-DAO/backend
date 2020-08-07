from . import *
from say.models import commit, session
from say.models import Invitation, Family
from ..schema.invitation import NewInvitationSchema


class InvitationAPI(Resource):

    @json
    @commit
    @swag_from('./docs/invitation/create.yml')
    def post(self):
        try:
            data = NewInvitationSchema(
                **request.form.to_dict(),
            )
        except ValueError as ex:
            return ex.json(), 400

        family_id = session.query(Family.id) \
            .filter_by(id=data.family_id) \
            .filter_by(isDeleted=False) \
            .one_or_none()

        if not family_id:
            return {'message': 'Family not found'}, 404

        role = data.role
        invitation = session.query(Invitation) \
            .filter_by(family_id=family_id) \
            .filter_by(role=role) \
            .one_or_none()

        if not invitation:
            invitation = Invitation(**data.dict())
            session.add(invitation)

        invitation.text = data.text
        return invitation


api.add_resource(InvitationAPI, "/api/v2/invitations/")

