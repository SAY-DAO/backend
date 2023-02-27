from say.roles import SOCIAL_WORKER
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


UNCONFIRM_NEED_URL = '/api/v2/needs/%s/unconfirm'


class TestUnconfirmNeed(BaseTestClass):
    def mockup(self):
        self.admin = self._create_random_sw(role=SUPER_ADMIN)
        self.sw1 = self._create_random_sw(role=SOCIAL_WORKER)

        self.c1 = self._create_random_child(sw=self.sw1)

    def test_unconfirm_need(self):
        self.confirmed_need = self._create_random_need(child=self.c1, isConfirmed=True)

        self.login_sw(self.admin)
        res = self.client.post(UNCONFIRM_NEED_URL % self.confirmed_need.id)
        self.assert_code(res, 200)
        assert res.json['isConfirmed'] is False
        assert res.json['confirmUser'] is None
        # assert res.json['unconfirmed_by_id'] == self.admin.id

    def test_unconfirm_deleted_need(self):
        self.login_sw(self.admin)

        deleted_need = self._create_random_need(child=self.c1, isDeleted=True)
        res = self.client.post(UNCONFIRM_NEED_URL % deleted_need.id)
        self.assert_code(res, 404)

    def test_unconfirm_unconfirmed_need(self):
        self.login_sw(self.admin)

        unconfirmed_need = self._create_random_need(child=self.c1, isConfirmed=False)
        res = self.client.post(UNCONFIRM_NEED_URL % unconfirmed_need.id)
        self.assert_code(res, 600)

    def test_unconfirm_delivered_need(self):
        self.login_sw(self.admin)
        delivered_need = self._create_random_need(
            child=self.c1, status=5, type=0, isReported=True
        )
        res = self.client.post(UNCONFIRM_NEED_URL % delivered_need.id)
        self.assert_code(res, 601)

    def test_unconfirm_need_as_sw(self):
        self.login_sw(self.sw1)
        self.confirmed_need = self._create_random_need(
            child=self.c1, status=1, isConfirmed=True
        )
        res = self.client.post(UNCONFIRM_NEED_URL % self.confirmed_need.id)
        self.assert_code(res, 403)
