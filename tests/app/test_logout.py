from tests.helper import UNAUTHORIZED_ERROR_CODE
from tests.helper import BaseTestClass


LOGOUT_URL = '/api/v2/auth/logout/token'


class TestLogout(BaseTestClass):
    def mockup(self):
        self.user = self._create_random_user()

    def test_logout(self):
        token = self.login(self.user)

        headers = {"Authorization": token}

        res = self.client.post(LOGOUT_URL, headers=headers)
        assert res.status_code == 200

    def test_logout_wrong_token(self):
        self.login(self.user)

        token = "gkshdfkasldjlsajdlshf"

        res = self.client.post(LOGOUT_URL, headers={"Authorization": token})
        assert res.status_code == UNAUTHORIZED_ERROR_CODE

    def test_logout_without_token(self):
        res = self.client.post(LOGOUT_URL)
        assert res.status_code == UNAUTHORIZED_ERROR_CODE
