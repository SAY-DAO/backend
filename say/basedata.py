from datetime import datetime

from say.orm import session, create_engine, bind_session
from say.models.user_model import User
from say.config import config


def basedata():
    engine = create_engine(config['dbUrl'])
    bind_session(engine)

    # Add Base data here #

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

    test_user = User(
        userName='test',
        password='test',
        emailAddress='test@say.company',
        avatarUrl='',
        firstName='test',
        lastName='test',
        city=1,  # Tehran
        country=1,  # Iran
        lastLogin=datetime.utcnow(),
    )
    session.add(test_user)

    try:
        session.commit()
    except:
        session.rollback()

