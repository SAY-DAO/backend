from . import *
from say.models import commit, session
from say.models import Invitation, InvitationForm


class InvitationAPI(Resource):

    @json
    @commit
    @swag_from('./docs/invitation/create.yml')
    def post(self):
        data = request.form
        form = InvitationForm(data)
        if not form.validate():
            return form.errors, 400

        invitation = Invitation(**form.data)
        session.add(invitation)

        return invitation


api.add_resource(InvitationAPI, "/api/v2/invitations/")
