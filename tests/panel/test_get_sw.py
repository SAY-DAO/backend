from say.roles import COORDINATOR
from say.roles import NGO_SUPERVISOR
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


GET_SW_URL = '/api/v2/socialworkers/%s'


class TestGetSocialWorker(BaseTestClass):
    def test_get_social_worker(self):
        admin = self.login_as_sw(role=SUPER_ADMIN)
        sw1 = self._create_random_sw()

        c1 = self._create_random_child(sw=admin)
        c2 = self._create_random_child(sw=sw1)
        self._create_random_child(sw=admin, isDeleted=True)
        self._create_random_child(sw=admin)
        self._create_random_need(child=c1, isConfirmed=True)
        self._create_random_need(child=c1, isConfirmed=True)
        self._create_random_need(child=c1, isConfirmed=False)
        self._create_random_need(child=c1, isDeleted=True)
        self._create_random_need(child=c2, isDeleted=False, isConfirmed=True)

        res = self.client.get(
            GET_SW_URL % admin.id,
        )

        self.assert_ok(res)
        assert res.json['id'] == admin.id
        assert res.json['firstName'] == admin.first_name
        assert res.json['lastName'] == admin.last_name
        assert res.json['avatarUrl'] == admin.avatar_url
        assert res.json['phoneNumber'] == admin.phone_number
        assert res.json['email'] == admin.email
        assert res.json['typeName'] == admin.privilege.name
        assert res.json['ngoName'] == admin.ngo.name
        assert res.json['childCount'] == 3
        assert res.json['currentChildCount'] == 2
        assert res.json['needCount'] == 4
        assert res.json['currentNeedCount'] == 2
        assert res.json['ngoName'] == admin.ngo.name
        assert res.json['city']['name'] is not None
        assert res.json['city']['countryName'] is not None
        assert 'password' not in res.json
        assert '_password' not in res.json

        res = self.client.get(
            GET_SW_URL % 'invalid_id',
        )

        self.assert_code(res, 404)

        deleted_sw = self._create_random_sw(is_deleted=True)
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
