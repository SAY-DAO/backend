# from datetime import datetime
#
# from say.models import User
# from tests.helper import ApplicableTestCase
#

from tests.helper import create_user


USER_URL = '/api/v2/user/%s'


def test_login_by_username(db, client):
    session = db()
    password = '123456'
    user = create_user(password)
    session.save(user)


# class TestGetUser(ApplicableTestCase):
#
#     @classmethod
#     def mockup(cls):
#         session = cls.create_session()
#         cls.password = '123456'
#         u = User(
#             userName='test',
#             emailAddress='test@test.com',
#             phone_number='+989990009900',
#             password=cls.password,
#             firstName='test',
#             lastName='test',
#             city=1,
#             country=1,
#             lastLogin=datetime.utcnow(),
#         )
#         session.add(u)
#         session.commit()
#         cls.user = u
#
#     def test_get(self):
#         a = self.login(self.user.userName, self.password)
#         assert a.status_code == 200
#         assert a.json['accessToken'] is not None
#         assert a.json['user']['id'] is not None
#
#
