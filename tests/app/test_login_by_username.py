from tests.helper import LOGIN_URL
from tests.helper import BaseTestClass


class TestLogin(BaseTestClass):
    def mockup(self):
        self.password = '123456'
        self.user = self.create_user(self.password)

    def test_login_by_username(self):
        res = self.client.post(
            LOGIN_URL,
            data={
                'username': self.user.userName,
                'password': self.password,
                'isInstalled': 0,
            }
        )
        assert res.status_code == 200
        assert res.json['accessToken'] is not None
        assert res.json['refreshToken'] is not None
        assert res.json['user']['id'] is not None

    def test_login_by_username_wrong_password(self):
        # when password is wrong
        res = self.client.post(
            LOGIN_URL,
            data={
                'username': self.user.userName,
                'password': 'wrong-password',
                'isInstalled': 0,
            },
        )
        assert res.status_code == 400

    def test_login_by_username_incomplete_parameter(self):
        res = self.client.post(
            LOGIN_URL,
            data={
                'username': self.user.userName,
                'password': self.password,
            },
        )
        assert res.status_code == 400
