from tests.helper import BaseTestClass


CHECK_EMAIL_URL = '/api/v2/check/email/%s'


class TestCheckEmail(BaseTestClass):
    def mockup(self):
        self.user = self.create_user()

    def test_check_username(self):
        res = self.client.get(
            CHECK_EMAIL_URL % 'abc@def.com',
        )
        assert res.status_code == 200

        res = self.client.get(
            CHECK_EMAIL_URL % ' abc@def.com ',
        )
        assert res.status_code == 200

        res = self.client.get(
            CHECK_EMAIL_URL % 'abc',
        )
        assert res.status_code == 720

        res = self.client.get(
            CHECK_EMAIL_URL % 'asd@gaae',
        )
        assert res.status_code == 720

        self.user.is_email_verified = True
        self.session.save(self.user)
        res = self.client.get(
            CHECK_EMAIL_URL % self.user.emailAddress,
        )
        assert res.status_code == 721

        res = self.client.get(
            CHECK_EMAIL_URL % (' ' + self.user.emailAddress),
        )
        assert res.status_code == 721

        self.user.is_email_verified = False
        self.session.save(self.user)
        res = self.client.get(
            CHECK_EMAIL_URL % self.user.emailAddress,
        )
        assert res.status_code == 721
