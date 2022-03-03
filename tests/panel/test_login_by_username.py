from tests.helper import BaseTestClass


PANEL_LOGIN_URL = '/api/v2/panel/auth/login'


class TestLogin(BaseTestClass):
    def mockup(self):
        self.password = 'password'
        self.user = self._create_random_sw(password=self.password)

    def test_login_by_username(self):
        res = self.client.post(
            PANEL_LOGIN_URL,
            data={
                'username': self.user.username,
                'password': self.password,
            },
        )
        self.assert_ok(res)
        assert res.json['access_token'] is not None
        assert res.json['refresh_token'] is not None
        assert res.json['id'] == self.user.id

    def test_login_by_username_wrong_password(self):
        # when password is wrong
        res = self.client.post(
            PANEL_LOGIN_URL,
            data={
                'username': self.user.username,
                'password': 'wrong-password',
            },
        )
        assert res.status_code == 303

    def test_login_by_username_incomplete_parameter(self):
        res = self.client.post(
            PANEL_LOGIN_URL,
            data={'username': self.user.username},
        )
        self.assert_code(res, 400)
