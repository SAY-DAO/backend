# from say.validations import VALID_ROLES
# from say.models import commit, session
# from say.models import PendingInvitation, Invitation
# from say.schema.user_invitation import NewPendingInvitationSchema
# from say import crud
#
# from . import *
#
#
# class UserInvitationAPI(Resource):
#
#     @authorize
#     @json
#     @commit
#     @swag_from('./docs/user_invitation/create.yml')
#     def post(self):
#         try:
#             data = NewPendingInvitationSchema(**request.form.to_dict())
#         except ValueError as e:
#             return e.json(), 400
#
#         if data.role not in VALID_ROLES:
#             return {'message': f'invalid role: {data.role}'}, 400
#
#         if not (user_id := crud.user.get_id_by_username(data.invited_username)):
#             return {'message': f'user {data.invited_username} not exists'}, 400
#
#         if not crud.family.exixts_by_id(data.family_id):
#             return {'message': f'family {data.family_id} not exists'}, 400
#
#         inviter_by_id = get_user_id()
#         invitation = Invitation(
#             family_id=data.family_id, invited_by_id=inviter_by_id, role=data.role,
#         )
#
#         user_invitation = PendingInvitation(
#             invitation=invitation, user_id=user_id, role=data.role,
#         )
#         session.add(user_invitation)
#
#         return user_invitation
#
#
# api.add_resource(
#     UserInvitationAPI,
#     '/v2/user_invitataion',
# )
