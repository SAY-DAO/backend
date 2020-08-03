from ..models import Invitation, session


def get_by_token(token):
    return session.query(Invitation) \
        .filter(Invitation.token==token) \
        .with_for_update() \
        .one_or_none()
