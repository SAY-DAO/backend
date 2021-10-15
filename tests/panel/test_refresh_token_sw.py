from tests.helper import REFRESH_TOKEN_KEY
from tests.helper import UNAUTHORIZED_ERROR_CODE
from tests.helper import BaseTestClass


REFRESH_TOKEN_SW_URL = '/api/v2/panel/auth/refresh'


class TestRefreshTokenSocialWorker(BaseTestClass):
    def test_refresh_token(self):
        self.login_as_sw()
        headers = {"Authorization": self._client.environ_base[REFRESH_TOKEN_KEY]}
        res = self.client.post(REFRESH_TOKEN_SW_URL, headers=headers)
        assert res.status_code == 200

    def test_invalid_refresh_token(self):
        self.login_as_sw()
        headers = {"Authorization": self._client.environ_base[REFRESH_TOKEN_KEY] + "fake"}
        res = self.client.post(REFRESH_TOKEN_SW_URL, headers=headers)
        assert res.status_code == UNAUTHORIZED_ERROR_CODE
