from hashlib import md5

from tests.helper import BaseTestClass


PANEL_LOGIN_URL = '/api/v2/panel/auth/login'


class TestLogin(BaseTestClass):
    def mockup(self):
        self.password = 'password'
        self.user = self.create_panel_user(self.password)

    def test_login_by_username(self):
        res = self.client.post(
            PANEL_LOGIN_URL,
            data={
                'username': self.user.userName,
                'password': self.password,
            }
        )
        assert res.status_code == 200
        assert res.json['access_token'] is not None
        assert res.json['refresh_token'] is not None

    def test_login_by_username_wrong_password(self):
        # when password is wrong
        res = self.client.post(
            PANEL_LOGIN_URL,
            data={
                'username': self.user.userName,
                'password': 'wrong-password',
            },
        )
        assert res.status_code == 400

    def test_login_by_username_incomplete_parameter(self):
        res = self.client.post(
            PANEL_LOGIN_URL,
            data={
                'username': self.user.userName
            },
        )
        assert res.status_code == 400
