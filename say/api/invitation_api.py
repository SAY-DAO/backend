from . import *
from say.models import commit, session
from say.models import Invitation, InvitationForm, Family


class InvitationAPI(Resource):

    @json
    @commit
    @swag_from('./docs/invitation/create.yml')
    def post(self):
        data = request.form
        form = InvitationForm(data)
        if not form.validate():
            return form.errors, 400

        family_id = session.query(Family.id) \
            .filter_by(id=form.data['family_id']) \
            .filter_by(isDeleted=False) \
            .one_or_none()

        if not family_id:
            return {'message': 'Family not found'}, 404

        invitation = Invitation(**form.data)
        session.add(invitation)

        return invitation


api.add_resource(InvitationAPI, "/api/v2/invitations/")

