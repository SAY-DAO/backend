from ..models import Invitation, session, InvitationStatus, User


def create(family_id, user_id, type_):
    say_id = session.query(User.id).filter(
        User.formated_username == 'say',
    ).one()

    invitation = session.query(Invitation).filter(
        Invitation.family_id == family_id,
        Invitation.status == InvitationStatus.pending,
        Invitation.inviter_id == say_id,
        Invitation.invitee_id == user_id,
    ).one_or_none()

    if not invitation:
        invitation = Invitation(
            inviter_id=say_id,
            invitee_id=user_id,
            family_id=family_id,
        )
        session.add(invitation)
        session.flush()

    search = dict(
        token=invitation.token,
        type_=type_,
    )
    return search
