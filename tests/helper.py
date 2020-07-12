from datetime import datetime
from random import randint

from say.models import User

TEST_DB_URL = 'postgresql://postgres:postgres@localhost/say_test'








def create_user(password='password'):
    seed = randint(100000, 9999999)
    user = User(
        userName=seed,
        emailAddress=f'{seed}test@test.com',
        phone_number=f'+989990{seed}',
        password=password,
        firstName=f'test{seed}',
        lastName=f'test{seed}',
        city=1,
        country=1,
        lastLogin=datetime.utcnow(),
    )
    return user



class TestCase:
    pass


# class ApplicableTestCase:
#     _app = app
#     _engine = None
#     _sessions = []
#     _authentication_token = None
#     __metadata__ = None
#     __session = None
#
#     @classmethod
#     def initialize_orm(cls):
#         # Drop the previously created db if exists.
#         with DBManager(url=TEST_DB_URL) as m:
#             m.drop_database()
#             m.create_database()
#
#         # An engine to create db schema and bind future created sessions
#         cls._engine = create_engine(TEST_DB_URL)
#
#         # A session factory to create and store session
#         # to close it on tear down
#         session = cls.create_session(expire_on_commit=False)
#
#         # Creating database objects
#         setup_schema(session)
#         session.commit()
#
#         # Closing the session to free the connection for future sessions.
#         session.close()
#
#     @classmethod
#     def mockup(cls):
#         """This is a template method so this is optional to override and you
#         haven't call the super when overriding it, because there isn't any.
#         """
#         pass
#
#     @classmethod
#     def cleanup_orm(cls):
#         # Closing all sessions created by the tests writer
#         while True:
#             try:
#                 s = cls._sessions.pop()
#                 s.close()
#             except IndexError:
#                 break
#
#         session.remove()
#         if cls._engine is not None:
#             cls._engine.dispose()
#
#         # Dropping the previousely created database
#         with DBManager(url=TEST_DB_URL) as m:
#             m.drop_database()
#
#     @classmethod
#     def setup_class(cls):
#         config['dbUrl'] = TEST_DB_URL
#         try:
#             cls.initialize_orm()
#             cls.mockup()
#         except:  # pragma: no cover
#             cls.teardown_class()
#             raise
#
#     @classmethod
#     def teardown_class(cls):
#         cls.cleanup_orm()
#
#     @property
#     def client(self):
#         return self._app.test_client()
#
#     def login(self, username, password):
#         return self.client.post(
#             '/api/v2/auth/login',
#             data={
#                 'username': username,
#                 'password': password,
#                 'isInstalled': 0,
#             },
#         )
#
#     def logout(self):
#         self._authentication_token = None


