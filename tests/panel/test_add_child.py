from random import randint

import ujson

from say.models import Child
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


ADD_CHILD_URL = '/api/v2/child/add/'


class TestAddChild(BaseTestClass):
    def test_add_child(self):
        admin = self.login_as_sw(role=SUPER_ADMIN)

        data = dict(
            firstName='asd',
            ngo_id=admin.ngo_id,
            sw_id=admin.id,
            telegramId=123456789,
            idNumber='12345666',
            gender='true',
            birthCertificateNumber='1234567890',
            phoneNumber=f'+98{randint(10000, 1000000)}',
            cityId=self._create_city().id,
            birthPlaceId=self._create_city().id,
            nationality=self._create_country().id,
            birthDate='1995-10-10',
            sayname_translations=ujson.dumps(dict(fa='asd', en='asd')),
            bio_translations=ujson.dumps(dict(fa='asd', en='asd')),
            bio_summary_translations=ujson.dumps(dict(fa='asd', en='asd')),
            emergencyPhoneNumber=f'+98{randint(10000, 1000000)}',
            awakeAvatarUrl=self.create_test_file('imageUrl.jpg', size=10000),
            sleptAvatarUrl=self.create_test_file('imageUrl.jpg', size=10000),
            voiceUrl=self.create_test_file('imageUrl.mp3', size=10000),
        )

        res = self.client.post(
            ADD_CHILD_URL,
            content_type='multipart/form-data',
            data=data,
        )

        self.assert_ok(res)
        assert res.json['id'] is not None
