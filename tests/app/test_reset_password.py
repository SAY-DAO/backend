from tests.helper import BaseTestClass

RESET_PASS_EMAIL_URL = '/api/v2/auth/password/reset/email'
RESET_PASS_PHONE_URL = '/api/v2/auth/password/reset/phone'


class TestResetPass(BaseTestClass):
    def mockup(self):
        self.password = '123456'
        self.user = self.create_user(self.password)

    def test_verify_phone(self):
        res = self.client.post(
            RESET_PASS_PHONE_URL,
            data={
                'phoneNumber': '+989999999'
            }
        )
        print(res.json['message'])
        assert res.status_code == 200

    def test_verify_wrong_phone(self):
        res = self.client.post(
            RESET_PASS_PHONE_URL,
            data={
                'phoneNumber': '0127616539'
            }
        )
        assert res.status_code == 400

    def test_reset_pass_email(self):
        res = self.client.post(
            RESET_PASS_EMAIL_URL,
            data={
                'email': 'test@test.com'
            }
        )
        assert res.status_code == 200

    def test_reset_pass_wrong_email(self):
        res = self.client.post(
            RESET_PASS_EMAIL_URL,
            data={
                'email': 'test@test'
            }
        )
        assert res.status_code == 400
