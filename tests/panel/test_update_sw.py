import pytest

from say.roles import ROLES
from say.roles import SAY_SUPERVISOR
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


UPDATE_SW_URL = '/api/v2/socialWorker/update/socialWorkerId=%s'


class TestUpdateSocialWorker(BaseTestClass):
    @pytest.mark.parametrize(
        'field,value,code',
        [
            ('firstName', 'new-str', 200),
            # (
            #     'id_type',
            #     1,
            #     200
            # ),
            ('lastName', 'new-str', 200),
            ('telegramId', '23432545234', 200),
            ('idNumber', '564564565465', 200),
            ('country', 1, 200),
            ('city', 1, 200),
            ('birthCertificateNumber', '9876523423441223', 200),
            # ('birthDate', '1999-12-12', 200), # TODO: current json encoder resulets "Sun, 12 Dec 1999 00:00:00 GMT"
            ('postalAddress', 'postalAddress', 200),
            ('bankAccountNumber', '231434523', 200),
            ('bankAccountShebaNumber', '12312343423566', 200),
            ('bankAccountCardNumber', '5645623434', 200),
            ('gender', False, 200),
            ('gender', True, 200),
            ('birthCertificateNumber', '76452334123', 200),
            ('phoneNumber', '+980213412414', 200),
            ('phoneNumber', '0213412414', 400),
            ('emergencyPhoneNumber', '+98054232434', 200),
            ('emergencyPhoneNumber', '8054232434', 400),
            ('emailAddress', 'newexample@test.com', 200),
            ('emailAddress', 'newexample@test', 400),
            ('emailAddress', 'newexample', 400),
            # ('id_ngo', admin.id_ngo)
            # ('avatarUrl', self.create_test_file('imageUrl.jpg', size=10000))
            # (
            #     'userName',
            #     'sw001035',
            #     200
            # ),
        ],
    )
    def test_update_social_worker(self, field, value, code):
        if isinstance(value, tuple):
            value, expected = value

        else:
            expected = value

        admin = self.login_as_sw(role=SUPER_ADMIN)

        res = self.client.patch(
            UPDATE_SW_URL % admin.id,
            content_type='multipart/form-data',
            data={
                field: value,
            },
        )

        assert res.status_code == code
        if code == 200:
            assert res.json.get(field) == expected

    def test_update_social_worker_ngo(self):
        admin = self.login_as_sw(role=SUPER_ADMIN)
        self._create_random_child(sw=admin)

        old_ngo = admin.ngo
        new_ngo = self._create_random_ngo()

        res = self.client.patch(
            UPDATE_SW_URL % admin.id,
            content_type='multipart/form-data',
            data={
                'id_ngo': new_ngo.id,
            },
        )

        assert res.status_code == 200
        assert res.json.get('id_ngo') == new_ngo.id

        self.session.expire(old_ngo)
        assert old_ngo.currentSocialWorkerCount == 0
        assert old_ngo.socialWorkerCount == 0
        assert old_ngo.currentChildrenCount == 0
        assert old_ngo.childrenCount == 0

        self.session.expire(new_ngo)
        assert new_ngo.currentSocialWorkerCount == 1
        assert new_ngo.socialWorkerCount == 1
        assert new_ngo.currentChildrenCount == 1
        assert new_ngo.childrenCount == 1

        for role in ROLES - {SUPER_ADMIN, SAY_SUPERVISOR}:
            user = self.login_as_sw(role=role)
            new_ngo = self._create_random_ngo()

            res = self.client.patch(
                UPDATE_SW_URL % user.id,
                content_type='multipart/form-data',
                data={
                    'id_ngo': new_ngo.id,
                },
            )

            assert res.status_code == 403

    def test_update_social_worker_with_invalid_id(self):
        self.login_as_sw(role=SUPER_ADMIN)

        res = self.client.patch(
            UPDATE_SW_URL % 'invalid-id',
            content_type='multipart/form-data',
            data={
                'firstName': 'new-str',
            },
        )

        assert res.status_code == 404

    def test_update_social_worker_password(self):
        admin = self.login_as_sw(role=SUPER_ADMIN)
        new_password = 'new-password'

        res = self.client.patch(
            UPDATE_SW_URL % admin.id,
            content_type='multipart/form-data',
            data={
                'password': new_password,
            },
        )

        assert res.status_code == 200
        self.session.refresh(admin)
        admin.validate_password(new_password)

        res = self.client.patch(
            UPDATE_SW_URL % admin.id,
            content_type='multipart/form-data',
            data={
                'password': 'weak',
            },
        )

        assert res.status_code == 400

    def test_update_social_worker_avatar(self):
        admin = self.login_as_sw(role=SUPER_ADMIN)

        res = self.client.patch(
            UPDATE_SW_URL % admin.id,
            content_type='multipart/form-data',
            data={
                'avatarUrl': self.create_test_file('image.jpg', size=10000),
            },
        )

        assert res.status_code == 200
        self.session.refresh(admin)
        assert res.json.get('avatarUrl') == admin.avatarUrl

        res = self.client.patch(
            UPDATE_SW_URL % admin.id,
            content_type='multipart/form-data',
            data={
                'avatarUrl': self.create_test_file('movie.mp3', size=10000),
            },
        )

        assert res.status_code == 400

    def test_update_social_worker_id_card(self):
        admin = self.login_as_sw(role=SUPER_ADMIN)

        res = self.client.patch(
            UPDATE_SW_URL % admin.id,
            content_type='multipart/form-data',
            data={
                'idCardUrl': self.create_test_file('image.jpg', size=10000),
            },
        )

        assert res.status_code == 200
        assert res.json.get('idCardUrl')
        self.session.refresh(admin)
        assert res.json.get('idCardUrl') == admin.idCardUrl

        res = self.client.patch(
            UPDATE_SW_URL % admin.id,
            content_type='multipart/form-data',
            data={
                'idCardUrl': self.create_test_file('movie.mp3', size=10000),
            },
        )

        assert res.status_code == 400

    def test_update_social_worker_passport(self):
        admin = self.login_as_sw(role=SUPER_ADMIN)

        res = self.client.patch(
            UPDATE_SW_URL % admin.id,
            content_type='multipart/form-data',
            data={
                'passportUrl': self.create_test_file('image.jpg', size=10000),
            },
        )
        assert res.status_code == 200
        assert res.json.get('passportUrl')
        self.session.refresh(admin)
        assert res.json.get('passportUrl') == admin.passportUrl

        res = self.client.patch(
            UPDATE_SW_URL % admin.id,
            content_type='multipart/form-data',
            data={
                'passportUrl': self.create_test_file('movie.mp3', size=10000),
            },
        )

        assert res.status_code == 400
