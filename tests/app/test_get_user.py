# from datetime import datetime
#
# from say.models import User
# from tests.helper import ApplicableTestCase
#
from datetime import datetime

from say.models import User
from tests.helper import BaseTestClass


USER_GET_URL = '/api/v2/user/userId=%s'


# def test_user_get(db, client):
#     session = db()
#     user = _create_random_user()
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
        self.pw = '123456'
        self.user = self._create_random_user(password=self.pw)

    def test_user_get_me(self):
        self.login(self.user.userName, self.pw)

        res = self.client.get(
            USER_GET_URL % 'me',
        )
        assert res.status_code == 200
        assert res.json['id'] == self.user.id

        # get user by id instead of me
        res = self.client.get(
            USER_GET_URL % 1,
        )
        assert res.status_code == 403

        # when logged out or unauthorized
        self.logout()
        res = self.client.get(
            USER_GET_URL % 'me',
        )
        assert res.status_code == 401
