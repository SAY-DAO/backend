from say.models import session, User


def get_say_id():
    return session.query(User.id).filter(
        User.formated_username == 'say',
    ).one()
