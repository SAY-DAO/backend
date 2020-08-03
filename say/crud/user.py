from ..models import User, session


def get_by_id(user_id):
    return session.query(User) \
        .filter(User.id == user_id) \
        .filter(User.isDeleted.is_(False)) \
        .with_for_update() \
        .one_or_none()


def get_by_username(username):
    return session.query(User) \
        .filter(User.userName == username) \
        .filter(User.isDeleted.is_(False)) \
        .with_for_update() \
        .one_or_none()


def id_by_username(username):
    return session.query(User.id) \
        .filter(User.userName == username) \
        .filter(User.isDeleted.is_(False)) \
        .scalar()


def exists_by_username(username):
    return session.query(User.id) \
        .filter(User.userName == username) \
        .filter(User.isDeleted.is_(False)) \
        .scalar() is not None