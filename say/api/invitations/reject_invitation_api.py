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
from say.schema.invitation import RejectInvitationSchema


class RejectInvitationAPI(Resource):

    @json
    @commit
    @authorize
    @swag_from("../docs/invitation/reject.yml")
    def post(self, token: str):
        user_id = get_user_id()

        try:
            data = RejectInvitationSchema(**request.form.to_dict())
        except ValueError as ex:
            return ex.json(), 400

        invitation = session.query(Invitation) \
            .filter(Invitation.token == token) \
            .filter(Invitation.invitee_id == user_id) \
            .filter(Invitation.status == InvitationStatus.pending.value) \
            .one_or_none()

        if not invitation:
            return {'message': 'Invitation not found'}, 404

        invitation.reject(data.reject_reason)
        return invitation


api.add_resource(RejectInvitationAPI, '/api/v2/invitations/<token>/reject')

