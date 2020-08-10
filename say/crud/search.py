from .user import get_say_id
from ..models import Invitation, session


def create(family_id, type_):
    say_id = get_say_id()

    invitation = session.query(Invitation).filter(
        Invitation.family_id == family_id,
        Invitation.role.is_(None),
        Invitation.inviter_id == say_id,
    ).one_or_none()

    if not invitation:
        invitation = Invitation(
            inviter_id=say_id,
            family_id=family_id,
        )
        session.add(invitation)
        session.flush()

    search = dict(
        token=invitation.token,
        type_=type_,
    )
    return search
