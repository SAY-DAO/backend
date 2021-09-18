from tests.helper import REFRESH_TOKEN_KEY
from tests.helper import UNAUTHORIZED_ERROR_CODE
from tests.helper import BaseTestClass


REFRESH_TOKEN_URL = '/api/v2/auth/refresh'


class TestRefreshToken(BaseTestClass):
    def mockup(self):
        self.password = '123456'
        self.user = self._create_random_user(password=self.password)

    def test_refresh_token(self):
        self.login(self.user.userName, self.password)
        headers = {"Authorization": self._client.environ_base[REFRESH_TOKEN_KEY]}
        res = self.client.post(
            REFRESH_TOKEN_URL,
            headers=headers
        )
        assert res.status_code == 200

    def test_invalid_refresh_token(self):
        self.login(self.user.userName, self.password)
        headers = {"Authorization": self._client.environ_base[REFRESH_TOKEN_KEY] + "fake"}
        res = self.client.post(
            REFRESH_TOKEN_URL,
            headers=headers
        )

        assert res.status_code == UNAUTHORIZED_ERROR_CODE
