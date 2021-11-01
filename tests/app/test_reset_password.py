from datetime import datetime
from datetime import timedelta

from tests.helper import BaseTestClass


RESET_PASS_EMAIL_URL = '/api/v2/auth/password/reset/email'
RESET_PASS_PHONE_URL = '/api/v2/auth/password/reset/phone'
RESET_PASS_CONFRIM_URL = '/api/v2/auth/password/reset/confirm/token=%s'


class TestResetPass(BaseTestClass):
    def mockup(self):
        self.user = self._create_random_user()

    def test_reset_pass_phone(self):
        res = self.client.post(RESET_PASS_PHONE_URL, data={'phoneNumber': '+989999999'})
        print(res.json['message'])
        assert res.status_code == 200

    def test_reset_pass_wrong_phone(self):
        res = self.client.post(RESET_PASS_PHONE_URL, data={'phoneNumber': '0127616539'})
        assert res.status_code == 400

    def test_reset_pass_email(self):
        res = self.client.post(RESET_PASS_EMAIL_URL, data={'email': 'test@test.com'})
        assert res.status_code == 200

    def test_reset_pass_wrong_email(self):
        res = self.client.post(RESET_PASS_EMAIL_URL, data={'email': 'test@test'})
        assert res.status_code == 400

    def test_confirm_reset_pass(self):
        reset_pass_object = self._create_reset_pass(user=self.user)
        new_pass = 'newpassword'
        res = self.client.post(
            RESET_PASS_CONFRIM_URL % reset_pass_object.token,
            data={
                'password': new_pass,
                'confirm_password': new_pass,
            },
        )
        assert res.status_code == 200
        assert self.user.validate_password(new_pass)
        assert 'accessToken' in res.json
        assert 'refreshToken' in res.json
        assert 'user' in res.json

        self.session.expire_all()
        assert reset_pass_object.is_used is True

    def test_confirm_reset_pass_token_is_used(self):
        reset_pass_object = self._create_reset_pass(user=self.user, is_used=True)

        res = self.client.post(
            RESET_PASS_CONFRIM_URL % reset_pass_object.token,
            data={
                'password': 'new_pass',
                'confirm_password': 'new_pass',
            },
        )
        assert res.status_code == 400

    def test_confirm_reset_pass_expired(self):
        reset_pass_object = self._create_reset_pass(
            expire_at=datetime.now() - timedelta(days=1),
            user=self.user,
        )
        assert reset_pass_object.is_expired is True
        res = self.client.post(
            RESET_PASS_CONFRIM_URL % reset_pass_object.token,
            data={
                'password': 'new_pass',
                'confirm_password': 'new_pass',
            },
        )
        assert res.status_code == 400

    def test_confirm_reset_pass_not_matched(self):
        reset_pass_object = self._create_reset_pass(user=self.user)
        res = self.client.post(
            RESET_PASS_CONFRIM_URL % reset_pass_object.token,
            data={
                'password': 'new_pass1',
                'confirm_password': 'new_pass2',
            },
        )
        assert res.status_code == 499

    def test_confirm_reset_pass_token_not_found(self):
        res = self.client.post(
            RESET_PASS_CONFRIM_URL % 'random-nonexsisting-token',
            data={
                'password': 'new_pass',
                'confirm_password': 'new_pass',
            },
        )
        assert res.status_code == 404

