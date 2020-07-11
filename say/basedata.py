from datetime import datetime

from say.orm import session
from say.models.user_model import User


def basedata():
    say_user = User(
        userName='SAY',
        password='#b!S:)EB?8h7PjxQ',
        emailAddress='say@say.company',
        avatarUrl='/public/resources/img/logo.png',
        firstName='SAY',
        lastName='',
        city=1,  # Tehran
        country=1,  # Iran
        lastLogin=datetime.utcnow(),
    )
    session.add(say_user)

    try:
        session.commit()
    except:
        session.rollback()

