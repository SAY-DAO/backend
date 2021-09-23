from tests.helper import BaseTestClass


SW_URL = '/api/v2/socialWorker/update/socialWorkerId=%s'


class TestUpdateSw(BaseTestClass):
    def mockup(self):
        self.password = 'password'
        self.user = self.create_panel_user(password=self.password)

    def test_login_by_username(self):
        self.login_sw(self.user.userName, self.password)

        new_pass = 'newpassword'
        res = self.client.patch(
            SW_URL % self.user.id,
            data={
                'password': new_pass,
            },
        )
        assert res.status_code == 200

        self.login_sw(self.user.userName, new_pass)
