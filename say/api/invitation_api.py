from flasgger import swag_from
from flask import request
from flask_restful import Resource

from say.models import Invitation, InvitationForm, Family
from ..decorators import json
from ..orm import session, commit


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

        role = form.data.get('role', None)
        invitation = session.query(Invitation) \
            .filter_by(family_id=family_id) \
            .filter_by(role=role) \
            .one_or_none()

        if not invitation:
            invitation = Invitation(**form.data)
            session.add(invitation)

        return invitation



