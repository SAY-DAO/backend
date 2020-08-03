from ..models import Family, session


def get_by_id(family_id):
    return session.query(Family) \
        .filter(Family.id == family_id) \
        .with_for_update() \
        .one_or_none()


def exists_by_id(family_id):
    return session.query(Family.id) \
        .filter(Family.id == family_id) \
        .filter(Family.isDeleted.is_(False)) \
        .scalar() is not None
