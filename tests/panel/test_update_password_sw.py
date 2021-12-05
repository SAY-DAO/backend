from tests.helper import BaseTestClass


SW_URL = '/api/v2/socialWorker/update/socialWorkerId=%s'


class TestUpdateSw(BaseTestClass):
    def mockup(self):
        self.sw = self.create_panel_user()

    def test_update_sw_password(self):
        self.login_sw(self.sw)

        new_pass = 'newpassword'
        res = self.client.patch(
            SW_URL % self.sw.id,
            data={
                'password': new_pass,
            },
        )
        assert res.status_code == 200
