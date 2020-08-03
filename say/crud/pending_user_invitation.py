# from ..models import PendingInvitation, session
#
#
# def get_by_user_invite_role(user_id, invitation_id, role):
#     return session.query(PendingInvitation) \
#         .filter(PendingInvitation.invitee_id == user_id) \
#         .filter(PendingInvitation.invitation_id==invitation_id) \
#         .filter(PendingInvitation.role==role) \
#         .with_for_update() \
#         .one_or_none()
#
