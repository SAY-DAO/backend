# from datetime import datetime
#
# from say.models import User
# from tests.helper import ApplicableTestCase
#
from datetime import datetime

from say.models import User
from tests.helper import create_user, BaseTestClass

USER_GET_URL = '/api/v2/user/%s'


# def test_user_get(db, client):
#     session = db()
#     user = create_user()
#     session.save(user)
#
#     res = client.post(
#         LOGIN_URL,
#         data={
#             'username': user.userName,
#             'password': password,
#             'isInstalled': 0,
#         },
#     )
#     assert res.status_code == 200
#     assert res.json['accessToken'] is not None
#     assert res.json['refreshToken'] is not None
#     assert res.json['user']['id'] is not None


class TestGetUser(BaseTestClass):

    def mockup(self):
        session = self.session
        self.password = '123456'
        u = User(
            userName='test',
            emailAddress='test@test.com',
            phone_number='+989990009900',
            password=self.password,
            firstName='test',
            lastName='test',
            city=1,
            country=1,
            lastLogin=datetime.utcnow(),
        )
        session.add(u)
        session.commit()
        self.user = u

    def test_get(self):
        assert self.user.id is not None
        #
        # a = self.login(self.user.userName, self.password)
        # assert a.status_code == 200
        # assert a.json['accessToken'] is not None
        # assert a.json['user']['id'] is not None

#
