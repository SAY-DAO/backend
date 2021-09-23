from say.crud.child import is_gone
from say.exceptions import HTTPException
from say.models import Family
from say.models import Invitation
from say.orm import session


def create_or_update(data, inviter_id):
    family_child_tuple = (
        session.query(Family.id, Family.id_child)
        .filter(
            Family.id == data.family_id,
            Family.isDeleted.is_(False),
        )
        .one_or_none()
    )

    if not family_child_tuple:
        raise HTTPException(700, 'Family not found')

    family_id, child_id = family_child_tuple
    if is_gone(child_id):
        raise HTTPException(700, 'Child is gone')

    role = data.role
    invitation = (
        session.query(Invitation)
        .filter(
            Invitation.family_id == family_id,
            Invitation.inviter_id == inviter_id,
            Invitation.role == role,
        )
        .one_or_none()
    )

    if not invitation:
        invitation = Invitation(**data.dict(), inviter_id=inviter_id)
        session.add(invitation)
        session.flush()

    invitation.text = data.text
    return invitation
