from say.models import session, Child


def is_gone(id_):
    return session.query(Child.id).filter(
        Child.id == id_,
        Child.existence_status != 1,
    ).scalar()
