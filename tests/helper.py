import os
import re
from os import path

import pytest
from sqlalchemy.orm.session import close_all_sessions

import say.orm
from run import app
from say.config import config
from .db import PostgreSQLManager as DBManager
from say.orm import setup_schema, session_factory, create_engine, init_model, \
    session


TEST_DB_URL = 'postgresql://postgres:postgres@localhost/say_test'
HERE = path.abspath(path.dirname(__file__))
DATA_DIRECTORY = path.abspath(path.join(HERE, '../../data'))


@pytest.fixture(scope='function')
def db():

    app.config['dbUrl'] = TEST_DB_URL

    # Drop the previously created db if exists.
    with DBManager(url=TEST_DB_URL) as m:
        m.drop_database()
        m.create_database()

    # An engine to create db schema and bind future created sessions
    engine = create_engine(TEST_DB_URL)

    # A session factory to create and store session to close it on tear down
    sessions = []

    def _connect(*a, expire_on_commit=False, **kw):
        new_session = session_factory(
            bind=engine,
            *a,
            expire_on_commit=expire_on_commit,
            **kw
        )
        sessions.append(new_session)
        return new_session

    session = _connect(expire_on_commit=True)

    # Creating database objects
    setup_schema(session)
    say.orm.commit()

    # Closing the session to free the connection for future sessions.
    session.close()

    # Preparing and binding the application shared scoped session, due the
    # some errors when a model trying use the mentioned session internally.
    init_model(engine)

    yield _connect

    # Closing all sessions created by the tests writer
    for s in sessions:
        s.close()

    close_all_sessions()
    engine.dispose()

    # Dropping the previously created database
    with DBManager(url=TEST_DB_URL) as m:
        m.drop_database()


class TestCase:
    pass


class ApplicableTestCase:
    _app = app
    _engine = None
    _sessions = []
    _authentication_token = None
    __metadata__ = None
    __session = None

    @classmethod
    def create_session(cls, *a, expire_on_commit=True, **kw):
        new_session = session_factory(
            bind=cls._engine,
            *a,
            expire_on_commit=expire_on_commit,
            **kw
        )
        cls._sessions.append(new_session)
        return new_session

    @property
    def _session(self):
        if self.__session is None:
            self.__session = self.create_session()

        return self.__session

    @classmethod
    def initialize_orm(cls):
        # Drop the previously created db if exists.
        with DBManager(url=TEST_DB_URL) as m:
            m.drop_database()
            m.create_database()

        # An engine to create db schema and bind future created sessions
        cls._engine = create_engine(TEST_DB_URL)

        # A session factory to create and store session
        # to close it on tear down
        session = cls.create_session(expire_on_commit=True)

        # Creating database objects
        setup_schema(session)
        session.commit()

        # Closing the session to free the connection for future sessions.
        session.close()

    @classmethod
    def mockup(cls):
        """This is a template method so this is optional to override and you
        haven't call the super when overriding it, because there isn't any.
        """
        pass

    @classmethod
    def cleanup_orm(cls):
        # Closing all sessions created by the tests writer
        while True:
            try:
                s = cls._sessions.pop()
                s.close()
            except IndexError:
                break

        session.remove()
        if cls._engine is not None:
            cls._engine.dispose()

        # Dropping the previousely created database
        with DBManager(url=TEST_DB_URL) as m:
            m.drop_database()

    @classmethod
    def setup_class(cls):
        try:
            cls.initialize_orm()
            cls.mockup()
        except:  # pragma: no cover
            cls.teardown_class()
            raise

    @classmethod
    def teardown_class(cls):
        cls.cleanup_orm()

    @property
    def client(self):
        self._app.config['dbUrl'] = TEST_DB_URL
        return self._app.test_client()

    def login(self, username, password):
        return self.client.post(
            '/api/v2/auth/login',
            data={
                'username': username,
                'password': password,
                'isInstalled': 0,
            },
        )

    def logout(self):
        self._authentication_token = None

