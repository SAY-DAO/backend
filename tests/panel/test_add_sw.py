from say.models import SocialWorker
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


ADD_SW_URL = '/api/v2/socialWorker/add'


class TestAddSocialWorker(BaseTestClass):
    def test_add_social_worker(self):
        admin = self.login_as_sw(role=SUPER_ADMIN)

        data = dict(
            firstName='asd',
            id=42,
            id_ngo=admin.id_ngo,
            id_type=1,
            lastName='qw',
            userName='sw001035',
            telegramId=123456789,
            idNumber='12345666',
            gender='true',
            birthCertificateNumber='1234567890',
            phoneNumber='+9809054829099',
            emergencyPhoneNumber='+9801231231231',
            emailAddress='example@test.com',
            avatarUrl=self.create_test_file('imageUrl.jpg', size=10000),
        )

        res = self.client.post(
            ADD_SW_URL,
            content_type='multipart/form-data',
            data=data,
        )

        assert res.status_code == 200
        assert res.json['id'] is not None
        assert res.json['gender'] is True
        assert res.json['generatedCode'] == '001002'
        assert res.json['userName'] == 'sw001002'
        assert res.json['registerDate'] is not None
        assert res.json['lastLoginDate'] is not None
        assert 'password' not in res.json

        sw = self.session.query(SocialWorker).filter_by(id=res.json['id']).one_or_none()
        assert sw is not None
        assert sw.ngo.currentSocialWorkerCount == 2
        assert sw.ngo.socialWorkerCount == 2

        data.update(
            avatarUrl=self.create_test_file('imageUrl.jpg', size=10000),
            gender='false',
        )
        res = self.client.post(
            ADD_SW_URL,
            content_type='multipart/form-data',
            data=data,
        )

        assert res.status_code == 200
        assert res.json['generatedCode'] == '001003'
        assert res.json['userName'] == 'sw001003'
        assert res.json['gender'] is False

        # TODO: Add more tests
