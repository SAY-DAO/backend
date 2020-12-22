from say.models import Child
from say.orm import session


def is_gone(id_):
    return session.query(Child.id).filter(
        Child.id == id_,
        Child.existence_status != 1,
    ).scalar()
