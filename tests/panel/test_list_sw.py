from say.config import configs
from say.roles import COORDINATOR
from say.roles import NGO_SUPERVISOR
from say.roles import SOCIAL_WORKER
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


LIST_SW_URL = '/api/v2/socialworkers/'


class TestListSocialWorker(BaseTestClass):
    def test_list_social_worker(self):
        # As admin
        self.login_as_sw(role=SUPER_ADMIN)
        self._create_random_sw()
        self._create_random_sw(is_deleted=True)

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
        sw1 = self._create_random_sw(first_name='bob')
        self._create_random_sw(first_name='bob')
        self._create_random_sw()

        res = self.client.get(LIST_SW_URL, query_string=dict(ngoId=sw1.ngo.id))
        self.assert_ok(res)
        result = res.json
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['id'] == sw1.id

        res = self.client.get(LIST_SW_URL, query_string=dict(ngoId=sw1.ngo.id))
        self.assert_ok(res)
        result = res.json
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['id'] == sw1.id

        res = self.client.get(LIST_SW_URL, query_string=dict(firstName='bob'))
        self.assert_ok(res)
        assert len(res.json) == 2

        res = self.client.get(LIST_SW_URL, query_string=dict(ngoId='invalid-id'))
        self.assert_code(res, 400)

        res = self.client.get(LIST_SW_URL, query_string=dict(invalid_key='invalid-id'))
        self.assert_code(res, 200)
        assert len(res.json) == 4

    def test_list_social_worker_pagination(self):
        self.login_as_sw(role=SUPER_ADMIN)
        for i in range(10):
            self._create_random_sw()

        res = self.client.get(
            LIST_SW_URL,
            headers={
                configs.PAGINATION_TAKE_HEADER_KEY: 5,
                configs.PAGINATION_SKIP_HEADER_KEY: 0,
            },
        )
        self.assert_ok(res)
        assert len(res.json) == 5
        prev_result = res.json

        res = self.client.get(
            LIST_SW_URL,
            headers={
                configs.PAGINATION_TAKE_HEADER_KEY: 100,
                configs.PAGINATION_SKIP_HEADER_KEY: 3,
            },
        )
        self.assert_ok(res)
        result = res.json
        assert len(result) == 8  # Total is 11, but we only get 8
        assert result[0]['id'] == prev_result[3]['id']

        res = self.client.get(
            LIST_SW_URL,
            headers={
                configs.PAGINATION_TAKE_HEADER_KEY: 5,
                configs.PAGINATION_SKIP_HEADER_KEY: 100000,
            },
        )
        self.assert_ok(res)
        assert len(res.json) == 0

        # Test default values
        res = self.client.get(LIST_SW_URL)
        self.assert_ok(res)
        assert len(res.json) == 11

        res = self.client.get(
            LIST_SW_URL,
            headers={
                configs.PAGINATION_TAKE_HEADER_KEY: 5,
                configs.PAGINATION_SKIP_HEADER_KEY: configs.POSTRGES_MAX_BIG_INT + 1,
            },
        )
        self.assert_code(res, 400)

        res = self.client.get(
            LIST_SW_URL,
            headers={
                configs.PAGINATION_TAKE_HEADER_KEY: configs.PAGINATION_MAX_TAKE + 1,
                configs.PAGINATION_SKIP_HEADER_KEY: 0,
            },
        )
        self.assert_code(res, 400)
