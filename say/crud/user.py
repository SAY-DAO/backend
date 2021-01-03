from say.models import User
from say.orm import session


def get_say_id():
    return session.query(User.id).filter(
        User.formated_username == 'say',
    ).one()
