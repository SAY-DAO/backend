from random import randint

from say.models import SocialWorker
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


ADD_SW_URL = '/api/v2/socialworkers/'


class TestAddSocialWorker(BaseTestClass):
    def test_add_social_worker(self):
        admin = self.login_as_sw(role=SUPER_ADMIN)
        city = self._create_city()

        data = dict(
            firstName='asd',
            ngoId=admin.ngo_id,
            typeId=1,
            lastName='qw',
            telegramId=123456789,
            idNumber='12345666',
            gender='true',
            birthCertificateNumber='1234567890',
            phoneNumber=f'+98{randint(10000, 1000000)}',
            emergencyPhoneNumber=f'+98{randint(10000, 1000000)}',
            email=f'{randint(10000, 1000000)}@test.com',
            avatarUrl=self.create_test_file('imageUrl.jpg', size=10000),
            cityId=city.id,
        )

        res = self.client.post(
            ADD_SW_URL,
            content_type='multipart/form-data',
            data=data,
        )

        self.assert_ok(res)
        assert res.json['id'] is not None
        assert res.json['gender'] is True
        assert res.json['generatedCode'] == '001002'
        assert res.json['username'] == 'sw001002'
        assert res.json['locale'] == 'fa'
        assert res.json['avatarUrl'].startswith('http')
        assert res.json['lastLoginDate'] is not None
        assert res.json['cityId'] == city.id
        assert 'password' not in res.json

        sw = self.session.query(SocialWorker).filter_by(id=res.json['id']).one_or_none()
        assert sw is not None
        assert sw.ngo.currentSocialWorkerCount == 2
        assert sw.ngo.socialWorkerCount == 2

        # TODO: Add more tests
