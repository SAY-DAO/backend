from datetime import datetime

from sqlalchemy.orm import scoped_session, sessionmaker


def basedata(db):
    from say.models.user_model import User

    # Creating DB Session
    session_factory = sessionmaker(
        db,
        autoflush=False,
        autocommit=False,
        expire_on_commit=True,
        twophase=False,
    )

    session = scoped_session(session_factory)

    # Inserting BaseData

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

