from tests.helper import BaseTestClass


CHECK_PHONE_URL = '/api/v2/check/phone/%s'


class TestCheckPhone(BaseTestClass):
    def mockup(self):
        self.user = self.create_user()

    def test_check_username(self):
        res = self.client.get(
            CHECK_PHONE_URL % '+9897312',
        )
        assert res.status_code == 200

        res = self.client.get(
            CHECK_PHONE_URL % ' +983213',
        )
        assert res.status_code == 200

        res = self.client.get(
            CHECK_PHONE_URL % 'abc',
        )
        assert res.status_code == 730

        res = self.client.get(
            CHECK_PHONE_URL % '983213',
        )
        assert res.status_code == 730

        self.user.is_phonenumber_verified = True
        self.session.save(self.user)
        res = self.client.get(
            CHECK_PHONE_URL % self.user.phone_number.e164,
        )
        assert res.status_code == 731

        res = self.client.get(
            CHECK_PHONE_URL % (' ' + self.user.phone_number.e164),
        )
        assert res.status_code == 731

        self.user.is_phonenumber_verified = False
        self.session.save(self.user)
        res = self.client.get(
            CHECK_PHONE_URL % self.user.phone_number.e164,
        )
        assert res.status_code == 731
