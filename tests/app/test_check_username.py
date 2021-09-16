from tests.helper import BaseTestClass


CHECK_USERNAME_URL = '/api/v2/check/username/%s'


class TestCheckUsername(BaseTestClass):
    def mockup(self):
        self.user = self.create_user()

    def test_check_username(self):
        res = self.client.get(
            CHECK_USERNAME_URL % 'abc.d1',
        )
        assert res.status_code == 200

        res = self.client.get(
            CHECK_USERNAME_URL % 'abcef',
        )
        assert res.status_code == 710

        res = self.client.get(
            CHECK_USERNAME_URL % '1abcef',
        )
        assert res.status_code == 710

        res = self.client.get(
            CHECK_USERNAME_URL % '.abcef',
        )
        assert res.status_code == 710

        res = self.client.get(
            CHECK_USERNAME_URL % 'abc',
        )
        assert res.status_code == 710

        res = self.client.get(
            CHECK_USERNAME_URL % 'abcd$',
        )
        assert res.status_code == 710

        res = self.client.get(
            CHECK_USERNAME_URL % ' abcde',
        )
        assert res.status_code == 710

        res = self.client.get(
            CHECK_USERNAME_URL % self.user.userName,
        )
        assert res.status_code == 711

        res = self.client.get(
            CHECK_USERNAME_URL % self.user.userName.upper(),
        )
        assert res.status_code == 711
