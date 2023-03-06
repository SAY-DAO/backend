from tests.helper import BaseTestClass


CHANGE_PASSWORD_SW_URL = '/api/v2/socialworkers/me/change-password'


class TestUChangePasswordSocialWorker(BaseTestClass):
    def mockup(self):
        self.password = 'asdaASDs@d2aC'
        self.sw = self._create_random_sw(password=self.password)

    def test_change_password_social_worker(self):
        self.login_sw(self.sw)
        new_pass = 'valueA@asd2'
        res = self.client.post(
            CHANGE_PASSWORD_SW_URL,
            data=dict(
                currentPassword=self.password,
                newPassword=new_pass,
            ),
        )
        self.assert_code(res, 200)

        self.session.expire(self.sw)
        assert self.sw.validate_password(new_pass)

    def test_change_password_social_worker_wrong(self):
        self.login_sw(self.sw)

        res = self.client.post(
            CHANGE_PASSWORD_SW_URL,
            data=dict(
                currentPassword='ascasdasd',
                newPassword='valueA@asd2',
            ),
        )
        self.assert_code(res, 600)

    def test_change_password_social_worker_weak(self):
        self.login_sw(self.sw)

        res = self.client.post(
            CHANGE_PASSWORD_SW_URL,
            data=dict(
                currentPassword=self.password,
                newPassword='1',
            ),
        )
        self.assert_code(res, 400)

        res = self.client.post(
            CHANGE_PASSWORD_SW_URL,
            data=dict(
                currentPassword=self.password,
                newPassword='1234567890123',
            ),
        )
        self.assert_code(res, 400)

        res = self.client.post(
            CHANGE_PASSWORD_SW_URL,
            data=dict(
                currentPassword=self.password,
                newPassword='asdasdqweqweqwe',
            ),
        )
        self.assert_code(res, 400)

        res = self.client.post(
            CHANGE_PASSWORD_SW_URL,
            data=dict(
                currentPassword=self.password,
                newPassword='12312asdasASD',
            ),
        )
        self.assert_code(res, 400)

        res = self.client.post(
            CHANGE_PASSWORD_SW_URL,
            data=dict(
                currentPassword=self.password,
                newPassword='@!#d12d12asdwsdas',
            ),
        )
        self.assert_code(res, 400)

        res = self.client.post(
            CHANGE_PASSWORD_SW_URL,
            data=dict(
                currentPassword=self.password,
                newPassword='@!#sdasddqASDASD',
            ),
        )
        self.assert_code(res, 400)
