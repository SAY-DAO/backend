from flasgger import swag_from
from flask import request
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restful import Resource
from flask_restful import abort
from sqlalchemy.orm import selectinload

from say import crud
from say.crud.family import join_family
from say.exceptions import HTTP_NOT_FOUND
from say.exceptions import HTTPException
from say.models import Child
from say.models import Family
from say.models import Invitation
from say.models import InvitationAccept
from say.models import User
from say.models import commit
from say.schema.invitation import InvitationSchemaV3

from ..authorization import authorize
from ..authorization import get_user_id
from ..crud.user import get_say_id
from ..decorators import json
from ..orm import session
from ..schema.invitation import NewInvitationSchema
from ..schema.invitation import NewInvitationSchemaV3
from . import logger
from .ext import api


class InvitationAPI(Resource):
    @json
    @commit
    @swag_from('./docs/invitation/create.yml')
    def post(self):
        try:
            inviter_id = get_user_id()
        except NoAuthorizationError:
            logger.info('random search: public')
            inviter_id = get_say_id()

        except Exception as e:
            # Any other error
            logger.info('random search: bad jwt')
            logger.info(str(e))
            abort(401)

        try:
            data = NewInvitationSchema(
                **request.form.to_dict(),
            )
        except ValueError as ex:
            return ex.json(), 400

        invitation = crud.invitation.create_or_update(data, inviter_id)
        return invitation


class InvitationAPIV3(Resource):
    @authorize
    @json
    @commit
    @swag_from('./docs/invitation/create-v3.yml')
    def post(self):
        try:
            data = NewInvitationSchemaV3(
                **request.form.to_dict(),
            )
        except ValueError as ex:
            return ex.json(), 400

        inviter_id = get_user_id()
        invitation = crud.invitation.create_or_update(data, inviter_id)
        return InvitationSchemaV3.from_orm(invitation)


class InvitationsV3(Resource):
    GONE_CHILD = HTTPException(743, 'Child is Gone')

    @json
    @swag_from('./docs/invitation/get-v3.yml')
    def get(self, token):
        invitation = (
            session.query(Invitation)
            .filter_by(token=token)
            .with_for_update()
            .one_or_none()
        )

        if not invitation:
            return HTTP_NOT_FOUND()

        family = session.query(Family).get(invitation.family_id)
        if not family or family.child.isDeleted:
            return self.GONE_CHILD

        child = (
            session.query(Child)
            .filter(Child.isDeleted.is_(False))
            .filter(Child.is_gone.is_(False))
            .filter(Child.id == family.id_child)
            .options(selectinload('family.members.user'))
            .one_or_none()
        )

        if child is None:
            return self.GONE_CHILD

        result = InvitationSchemaV3.from_orm(invitation)
        return result


class InvitationsAcceptV3(Resource):
    @authorize
    @commit
    @json
    @swag_from('./docs/invitation/accept-v3.yml')
    def post(self, token):
        user_id = get_user_id()

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

        join_family(id_family, user_role, user)
        invitation_accept = InvitationAccept(
            invitation=invitation,
            invitee=user,
            role=user_role,
        )
        invitation.accepts.append(invitation_accept)
        return invitation


api.add_resource(InvitationAPI, "/api/v2/invitations/")
api.add_resource(InvitationAPIV3, "/api/v3/invitations/")
api.add_resource(
    InvitationsV3,
    '/api/v3/invitations/<token>',
)
api.add_resource(
    InvitationsAcceptV3,
    '/api/v3/invitations/<token>/accept',
)
