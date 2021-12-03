import shutil
import tempfile
from random import randint

import pytest
import sqlalchemy.orm.session
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


# class CustomClient(FlaskClient):
#     def __init__(self, *args, **kwargs):
#         self._authorization = kwargs.pop("authorization")
#         super(CustomClient, self).__init__(*args, **kwargs)
#
#
# app.test_client_class = CustomClient
# client = app.test_client(authentication='Basic ....')


@pytest.fixture
def flask_app():
    from say.api.ext import limiter
    from say.app import app
    from say.config import configs

    configs.UPLOAD_FOLDER = tempfile.mkdtemp()
    app.testing = True
    limiter.enabled = False
    return app


@pytest.fixture
def client(flask_app):
    print(2)
    from say.app import app
    from say.config import configs

    with app.test_client() as client:
        # if token := client._authorization:
        #     client.environ_base['Authorization'] = f'Bearer {token}'

        yield client

    shutil.rmtree(configs.UPLOAD_FOLDER)


# From https://github.com/pylover/restfulpy/blob/84b48fcd57fe08641d96a4aa3588887bd94d7f47/restfulpy/testing.py#L68
@pytest.fixture(scope='function')
def db():
    from say.config import configs
    from say.db import PostgreSQLManager as DBManager
    from say.orm import create_engine
    from say.orm import init_model
    from say.orm import setup_schema

    db_url = configs.postgres_test_url + str(
        randint(1000 * 1000 * 1000, 9 * 1000 * 1000 * 1000)
    )
    # Drop the previously created db if exists.
    with DBManager(url=db_url, admin_url=configs.postgres_admin_url) as m:
        m.drop_database()
        m.create_database()

    # An engine to create db schema and bind future created sessions
    # NullPool used to disable Connection Pool
    engine = create_engine(db_url, poolclass=NullPool)

    # A session factory to create and store session to close it on tear down
    sessions = []

    def _connect(*a, expire_on_commit=True, **kw):
        session_factory = sessionmaker(
            bind=engine, *a, expire_on_commit=expire_on_commit, **kw
        )
        new_session = scoped_session(session_factory)
        sessions.append(new_session)

        # Just for testing, don't do this at base code
        def save(x):
            new_session.add(x)
            new_session.commit()

        new_session.save = save
        return new_session

    session = _connect(expire_on_commit=True)

    # Creating database objects
    setup_schema(session)
    session.commit()

    # Removing the session to free the connection for future sessions.
    session.remove()

    # Preparing and binding the application shared scoped session, due the
    # some errors when a model trying use the mentioned session internally.
    init_model(engine)

    yield _connect

    # Closing all sessions created by the tests writer
    for s in sessions:
        s.remove()

    sqlalchemy.orm.session.close_all_sessions()
    engine.dispose()

    # Dropping the previously created database
    with DBManager(
        url=configs.postgres_test_url, admin_url=configs.postgres_admin_url
    ) as m:
        m.drop_database()
