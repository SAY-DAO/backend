from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restful import abort

from . import *
from say.models import commit, session
from say.models import Invitation, Family
from .. import crud
from ..crud.user import get_say_id
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

        try:
            inviter_id = get_user_id()
        except NoAuthorizationError:
            logger.info('random search: public')
            inviter_id = get_say_id()

        except Exception as e:
            # Any other error
            logger.info('random search: bad jwt')
            logger.info(str(e))
            abort(403)

        family_child_tuple = session.query(Family.id, Family.id_child).filter(
            Family.id == data.family_id,
            Family.isDeleted.is_(False),
        ).one_or_none()

        if not family_child_tuple:
            return {'message': 'Family not found'}, 404

        family_id, child_id = family_child_tuple
        if crud.child.is_gone(child_id):
            return {'message': 'child is gone'}, 700

        role = data.role
        invitation = session.query(Invitation).filter(
            Invitation.family_id == family_id,
            Invitation.inviter_id == inviter_id,
            Invitation.role == role,
        ).one_or_none()

        if not invitation:
            invitation = Invitation(**data.dict(), inviter_id=inviter_id)
            session.add(invitation)

        invitation.text = data.text
        return invitation


api.add_resource(InvitationAPI, "/api/v2/invitations/")

