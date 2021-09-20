from say.exceptions import HTTPException
from say.models import Family
from say.models import NeedFamily
from say.models import UserFamily
from say.orm import session
from say.validations import VALID_ROLES

from ..config import configs


def join_family(family_id, role, user):
    family = session.query(Family).with_for_update().get(family_id)

    if role not in VALID_ROLES:
        raise HTTPException(742, 'Invalid Role')
    elif (
        not family
        or family.child.isDeleted
        or family.child.isConfirmed is False
        or family.child.is_gone
    ):
        raise HTTPException(404, f'family {family_id} not found')

    elif not family.is_in_family(user):
        raise HTTPException(747, 'You already joined')

    elif not family.can_join(role):
        raise HTTPException(744, 'Can not join this family')

    user_family = (
        session.query(UserFamily)
        .filter_by(id_user=user.id)
        .filter_by(id_family=family_id)
        .first()
    )

    if not user_family:
        if not user.is_installed:
            family_count = (
                session.query(UserFamily).filter(UserFamily.id_user == user.id).count()
            )

            if family_count == 0:
                user.send_installion_notif(configs.ADD_TO_HOME_URL)

        new_member = UserFamily(
            user=user,
            family=family,
            userRole=role,
        )
        session.add(new_member)

    else:
        if user_family.userRole != role:
            raise HTTPException(
                746, f'You must back to your previous role: {user_family.userRole}'
            )

        user_family.isDeleted = False
        participations = (
            session.query(NeedFamily)
            .filter(NeedFamily.id_user == user.id)
            .filter(NeedFamily.id_family == family.id)
        )

        for p in participations:
            p.isDeleted = False

    family.child.sayFamilyCount += 1
    return family
