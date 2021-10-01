from tests.helper import BaseTestClass


USER_GET_URL = '/api/v2/user/userId=%s'


class TestGetUser(BaseTestClass):
    def mockup(self):
        self.pw = '123456'
        self.user = self._create_random_user(password=self.pw)

    def test_user_get_me(self):
        self.login(self.user.userName, self.pw)

        res = self.client.get(
            USER_GET_URL % 'me',
        )
        assert res.status_code == 200
        assert res.json['id'] == self.user.id

        # get user by id instead of me
        res = self.client.get(
            USER_GET_URL % 1,
        )
        assert res.status_code == 403

        # when logged out or unauthorized
        self.logout()
        res = self.client.get(
            USER_GET_URL % 'me',
        )
        assert res.status_code == 401
