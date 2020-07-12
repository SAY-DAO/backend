import os
import tempfile
from random import randint

import pytest
import sqlalchemy.orm.session

from say.app import app
from say.config import config
from say.orm import setup_schema, session_factory, create_engine, init_model
from say.db import PostgreSQLManager as DBManager

from flask.testing import FlaskClient


# class CustomClient(FlaskClient):
#     def __init__(self, *args, **kwargs):
#         self._authorization = kwargs.pop("authorization")
#         super(CustomClient, self).__init__(*args, **kwargs)
#
#
# app.test_client_class = CustomClient
# client = app.test_client(authentication='Basic ....')


TEST_DB_URL = 'postgresql://postgres:postgres@localhost/say_test'


@pytest.fixture
def client():
    config['dbUrl'] = TEST_DB_URL
    config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    config['TESTING'] = True
    app.testing = True
    with app.test_client() as client:
        # if token := client._authorization:
        #     client.environ_base['Authorization'] = f'Bearer {token}'

        yield client
        os.rmdir(config['UPLOAD_FOLDER'])


@pytest.fixture(scope='function')
def db():
    # Drop the previously created db if exists.
    with DBManager(url=TEST_DB_URL) as m:
        m.drop_database()
        m.create_database()

    # An engine to create db schema and bind future created sessions
    engine = create_engine(TEST_DB_URL)

    # A session factory to create and store session to close it on tear down
    sessions = []

    def _connect(*a, expire_on_commit=True, **kw):
        new_session = session_factory(
            bind=engine,
            *a,
            expire_on_commit=expire_on_commit,
            **kw
        )
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

    # Closing the session to free the connection for future sessions.
    session.close()

    # Preparing and binding the application shared scoped session, due the
    # some errors when a model trying use the mentioned session internally.
    init_model(engine)

    yield _connect

    # Closing all sessions created by the tests writer
    for s in sessions:
        s.close()

    sqlalchemy.orm.session.close_all_sessions()
    engine.dispose()

    # Dropping the previously created database
    with DBManager(url=TEST_DB_URL) as m:
        m.drop_database()
