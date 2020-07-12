from tests.helper import BaseTestClass

LOGIN_URL = '/api/v2/auth/login'


class TestLogin(BaseTestClass):
    def mockup(self):
        self.password = '123456'
        self.user = self.create_user(self.password)

    def test_login_by_username(self, client):

        res = client.post(
            LOGIN_URL,
            data={
                'username': self.user.userName,
                'password': self.password,
                'isInstalled': 0,
            },
        )
        assert res.status_code == 200
        assert res.json['accessToken'] is not None
        assert res.json['refreshToken'] is not None
        assert res.json['user']['id'] is not None

        # when password is wrong
        res = client.post(
            LOGIN_URL,
            data={
                'username': self.user.userName,
                'password': 'wrong-password',
                'isInstalled': 0,
            },
        )
        assert res.status_code == 400

    # TODO: and more...
