from say.roles import COORDINATOR
from say.roles import NGO_SUPERVISOR
from say.roles import SOCIAL_WORKER
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


LIST_SW_CREATED_NEEDS_URL = '/api/v2/socialworkers/%s/createdNeeds'


class TestListSocialWorkerCreatedNeeds(BaseTestClass):
    def test_list_sw_created_needs(self):
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
            LIST_SW_CREATED_NEEDS_URL % admin.id,
        )

        self.assert_ok(res)
        assert isinstance(res.json, list)
        assert len(res.json) == 3

        res = self.client.get(
            LIST_SW_CREATED_NEEDS_URL % 'invalid_id',
        )

        self.assert_code(res, 404)

        deleted_sw = self._create_random_sw(is_deleted=True)
        res = self.client.get(
            LIST_SW_CREATED_NEEDS_URL % deleted_sw.id,
        )
        self.assert_code(res, 404)

        same_ngo_sw = self._create_random_sw(ngo=sw1.ngo, role=SOCIAL_WORKER)
        self.login_sw(same_ngo_sw)

        res = self.client.get(
            LIST_SW_CREATED_NEEDS_URL % sw1.id,
        )
        self.assert_code(res, 404)

        self.login_sw(sw1)
        res = self.client.get(
            LIST_SW_CREATED_NEEDS_URL % sw1.id,
        )
        self.assert_ok(res)
        assert isinstance(res.json, list)
        assert len(res.json) == 1

    def test_list_social_worker_created_needs_by_coordinator_or_supervisor(self):
        for role in {COORDINATOR, NGO_SUPERVISOR}:
            sw = self.login_as_sw(role=role)

            sw_with_same_ngo = self._create_random_sw(ngo=sw.ngo)
            res = self.client.get(LIST_SW_CREATED_NEEDS_URL % sw_with_same_ngo.id)
            self.assert_ok(res)

            sw_another_ngo = self._create_random_sw()
            res = self.client.get(LIST_SW_CREATED_NEEDS_URL % sw_another_ngo.id)
            self.assert_code(res, 404)
