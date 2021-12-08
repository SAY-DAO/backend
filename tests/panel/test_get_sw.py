from say.roles import COORDINATOR
from say.roles import NGO_SUPERVISOR
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


GET_SW_URL = '/api/v2/socialWorker/socialWorkerId=%s'


class TestGetSocialWorker(BaseTestClass):
    def test_get_social_worker(self):
        admin = self.login_as_sw(role=SUPER_ADMIN)

        res = self.client.get(
            GET_SW_URL % admin.id,
        )

        self.assert_ok(res)
        assert res.json['id'] == admin.id
        assert res.json['firstName'] == admin.firstName
        assert res.json['lastName'] == admin.lastName
        assert res.json['avatarUrl'] == admin.avatarUrl
        assert res.json['phoneNumber'] == admin.phoneNumber
        assert res.json['emailAddress'] == admin.emailAddress
        assert res.json['typeName'] == admin.privilege.name
        assert res.json['ngoName'] == admin.ngo.name
        assert 'password' not in res.json
        assert '_password' not in res.json

        res = self.client.get(
            GET_SW_URL % 'invalid_id',
        )

        self.assert_code(res, 404)

        deleted_sw = self._create_random_sw(isDeleted=True)
        res = self.client.get(
            GET_SW_URL % deleted_sw.id,
        )
        self.assert_code(res, 404)

    def test_get_social_worker_by_coordinator_or_supervisor(self):
        for role in {COORDINATOR, NGO_SUPERVISOR}:
            sw = self.login_as_sw(role=role)

            sw_with_same_ngo = self._create_random_sw(ngo=sw.ngo)
            res = self.client.get(GET_SW_URL % sw_with_same_ngo.id)
            self.assert_ok(res)

            sw_another_ngo = self._create_random_sw()
            res = self.client.get(GET_SW_URL % sw_another_ngo.id)
            self.assert_code(res, 404)
