from datetime import datetime

from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


ADD_SW_URL = '/api/v2/socialWorker/add'


class TestAddSocialWorker(BaseTestClass):
    def test_add_social_worker(self):
        self.login_as_sw(role=SUPER_ADMIN)

        data = dict(
            firstName='asd',
            id=42,
            id_ngo=1,
            id_type=1,
            lastName='qw',
            userName='sw001035',
            telegramId=123456789,
            idNumber='12345666',
            gender='true',
            phoneNumber='123123123',
            emergencyPhoneNumber='1231231231',
            emailAddress='example@test.com',
            avatarUrl=self.create_test_file('imageUrl.jpg'),
        )

        res = self.client.post(
            ADD_SW_URL,
            content_type='multipart/form-data',
            data=data,
        )
        assert res.status_code == 200
        assert 'password' not in res.json
        # TODO: Add more tests
