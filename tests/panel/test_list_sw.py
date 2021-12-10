from say.roles import COORDINATOR
from say.roles import NGO_SUPERVISOR
from say.roles import SOCIAL_WORKER
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


LIST_SW_URL = '/api/v2/socialWorkers/'


class TestListSocialWorker(BaseTestClass):
    def test_list_social_worker(self):
        # As admin
        self.login_as_sw(role=SUPER_ADMIN)
        self._create_random_sw()
        self._create_random_sw(isDeleted=True)

        res = self.client.get(LIST_SW_URL)
        self.assert_ok(res)
        result = res.json
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]['id'] == 1

        # As supervisor
        supervisor = self.login_as_sw(role=NGO_SUPERVISOR)
        self._create_random_sw(ngo=supervisor.ngo)
        res = self.client.get(LIST_SW_URL)
        self.assert_ok(res)
        assert len(res.json) == 2

        # As coordinator
        coordinator = self.login_as_sw(role=COORDINATOR)
        self._create_random_sw(ngo=coordinator.ngo)
        res = self.client.get(LIST_SW_URL)
        self.assert_ok(res)
        assert len(res.json) == 2

        # As social worker
        self.login_as_sw(role=SOCIAL_WORKER)
        res = self.client.get(LIST_SW_URL)
        self.assert_code(res, 403)

        # As user
        self.login_as_user()
        res = self.client.get(LIST_SW_URL)
        self.assert_code(res, 403)

    def test_list_social_worker_filtering(self):
        # As admin
        self.login_as_sw(role=SUPER_ADMIN)
        sw1 = self._create_random_sw(firstName='bob')
        self._create_random_sw(firstName='bob')
        self._create_random_sw()

        res = self.client.get(LIST_SW_URL, query_string=dict(id_ngo=sw1.ngo.id))
        self.assert_ok(res)
        result = res.json
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['id'] == sw1.id

        res = self.client.get(LIST_SW_URL, query_string=dict(id_ngo=sw1.ngo.id))
        self.assert_ok(res)
        result = res.json
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['id'] == sw1.id

        res = self.client.get(LIST_SW_URL, query_string=dict(firstName='bob'))
        self.assert_ok(res)
        assert len(res.json) == 2

        res = self.client.get(LIST_SW_URL, query_string=dict(id_ngo='invalid-id'))
        self.assert_code(res, 400)

        res = self.client.get(LIST_SW_URL, query_string=dict(invalid_key='invalid-id'))
        self.assert_code(res, 400)
