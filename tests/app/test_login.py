from tests.helper import LOGIN_URL
from tests.helper import BaseTestClass


class TestLogin(BaseTestClass):
    def mockup(self):
        self.password = '123456'
        self.user = self._create_random_user(
            password=self.password,
            is_email_verified=True,
            is_phonenumber_verified=True,
        )

    def test_login_by_username(self):
        res = self.client.post(
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

        res = self.client.post(
            LOGIN_URL,
            data={
                'username': self.user.userName.upper(),
                'password': self.password,
                'isInstalled': 0,
            },
        )
        assert res.status_code == 200

        res = self.client.post(
            LOGIN_URL,
            data={
                'username': self.user.userName.lower(),
                'password': self.password,
                'isInstalled': 0,
            },
        )
        assert res.status_code == 200

    def test_login_by_email(self):
        data = {
            'username': self.user.emailAddress,
            'password': self.password,
            'isInstalled': 0,
        }

        res = self.client.post(
            LOGIN_URL,
            data=data,
        )
        assert res.status_code == 200
        assert res.json['accessToken'] is not None
        assert res.json['refreshToken'] is not None
        assert res.json['user']['id'] is not None

        self.user.is_email_verified = False
        self.session.save(self.user)
        res = self.client.post(
            LOGIN_URL,
            data=data,
        )
        assert res.status_code == 400

    def test_login_by_phone(self):
        data = {
            'username': self.user.phone_number.e164,
            'password': self.password,
            'isInstalled': 0,
        }

        res = self.client.post(
            LOGIN_URL,
            data=data,
        )
        assert res.status_code == 200
        assert res.json['accessToken'] is not None
        assert res.json['refreshToken'] is not None
        assert res.json['user']['id'] is not None

        self.user.is_phonenumber_verified = False
        self.session.save(self.user)
        res = self.client.post(
            LOGIN_URL,
            data=data,
        )
        assert res.status_code == 400

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

        res = self.client.post(
            LOGIN_URL,
            data={
                'username': self.user.userName,
                'isInstalled': 0,
            },
        )
        assert res.status_code == 400

        res = self.client.post(
            LOGIN_URL,
            data={
                'password': self.password,
                'isInstalled': 0,
            },
        )
        assert res.status_code == 400
