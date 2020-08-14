from tests.helper import BaseTestClass

PANEL_LOGIN_URL = '/api/v2/panel/auth/login'


class TestLogin(BaseTestClass):
    def mockup(self):
        self.password = '123456'
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
        assert res.json['accessToken'] is not None
        assert res.json['refreshToken'] is not None
        assert res.json['user']['id'] is not None
