from tests.helper import UNAUTHORIZED_ERROR_CODE
from tests.helper import BaseTestClass


LOGOUT_URL = '/api/v2/auth/logout/token'


class TestLogout(BaseTestClass):
    def mockup(self):
        self.password = '123456'
        self.user = self.create_user(self.password)

    def test_logout(self):
        token = self.login(self.user.userName, self.password)

        headers = {"Authorization": token}

        res = self.client.post(
            LOGOUT_URL,
            headers=headers
        )
        assert res.status_code == 200

    def test_logout_wrong_token(self):
        self.login(self.user.userName, self.password)

        token = "gkshdfkasldjlsajdlshf"

        res = self.client.post(
            LOGOUT_URL,
            headers={
                "Authorization": token
            }
        )
        assert res.status_code == UNAUTHORIZED_ERROR_CODE

    def test_logout_without_token(self):
        res = self.client.post(
            LOGOUT_URL
        )
        assert res.status_code == UNAUTHORIZED_ERROR_CODE
