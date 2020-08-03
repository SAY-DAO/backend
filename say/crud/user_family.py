from ..models import UserFamily, User, session
from ..validations import VALID_ROLES


class UserAlreadyInFamily(Exception):
    pass


class NoAvailableRole(Exception):
    pass


def is_user_in_family(family_id: int, user_id: int):
    return session.query(UserFamily.id) \
        .filter(UserFamily.id_family == family_id) \
        .filter(UserFamily.id_user == user_id) \
        .filter(UserFamily.isDeleted.is_(False)) \
        .scalar() is not None


# TODO: optimize
def available_roles(family_id: int, username: str):

    user_roles = session.query(UserFamily.userRole, UserFamily.isDeleted) \
        .filter(User.userName == username) \
        .join(User, User.id == UserFamily.id_user) \
        .filter(UserFamily.id_family == family_id) \
        .all()

    previous_role = None
    for role, is_deleted in user_roles:
        if not is_deleted:
            raise UserAlreadyInFamily()

    if user_roles:
        previous_role = user_roles[0].userRole

    if previous_role:
        valid_roles = {previous_role}
    else:
        valid_roles = set(VALID_ROLES)

    possible_father_mother = session.query(UserFamily.userRole) \
        .filter(UserFamily.id_family == family_id) \
        .filter(UserFamily.isDeleted.is_(False)) \
        .all()

    roles = valid_roles - set(possible_father_mother)
    if not roles:
        raise NoAvailableRole()

    return roles
