from tests.helper import BaseTestClass

VERIFY_PHONE_URL = '/api/v2/auth/verify/phone'
VERIFY_EMAIL_URL = '/api/v2/auth/verify/email'


class TestVerify(BaseTestClass):
    def test_verify_phone(self):
        res = self.client.post(
            VERIFY_PHONE_URL,
            data={
                'phone_number': '+989999999'
            }
        )
        assert res.status_code == 200

    def test_verify_wrong_phone(self):
        res = self.client.post(
            VERIFY_PHONE_URL,
            data={
                'phone_number': '9127616539'
            }
        )
        assert res.status_code == 400

    def test_verify_exist_phone(self):
        user = self.create_user('123456')
        res = self.client.post(
            VERIFY_PHONE_URL,
            data={
                'phone_number': '+98' + user.phone_number.__str__()
            }
        )

        assert res.status_code == 422

    def test_verify_email(self):
        res = self.client.post(
            VERIFY_EMAIL_URL,
            data={
                'email': 'test@test.com'
            }
        )
        assert res.status_code == 200

    def test_verify_wrong_email(self):
        res = self.client.post(
            VERIFY_EMAIL_URL,
            data={
                'email': 'test@test'
            }
        )
        assert res.status_code == 400

    def test_verify_missing_email(self):
        res = self.client.post(
            VERIFY_EMAIL_URL,
            data={
                'emailiii': 'test@test.com'
            }
        )
        assert res.status_code == 400

    def test_verify_exist_email(self):
        user = self.create_user('123456')

        res = self.client.post(
            VERIFY_EMAIL_URL,
            data={
                'email': user.emailAddress
            }
        )

        assert res.status_code == 422
