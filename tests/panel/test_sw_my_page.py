import pytest

from say.roles import ADMIN
from say.roles import ROLES
from say.roles import SAY_SUPERVISOR
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


SW_MY_PAGE_URL = '/api/v2/socialworkers/my-page'


class TestSocialWorkerMyPage(BaseTestClass):
    def mockup(self):
        self.sw = self._create_random_sw()
        self.child1 = self._create_random_child(sw=self.sw, isDeleted=False, existence_status=1)
        self.child2 = self._create_random_child(sw=self.sw, isDeleted=False, existence_status=1)
        self._create_random_need(child=self.child1)
        self._create_random_need(child=self.child1)
        self._create_random_need(child=self.child1)
        self._create_random_need(child=self.child2)

    def test_social_worker_my_page(self):
        self.login_sw(self.sw)

        res = self.client.get(
            SW_MY_PAGE_URL,
        )

        self.assert_code(res, 200)
        children = res.json
        assert 'id' in children[0]
        assert 'sayName' in children[0]
        assert 'firstName' in children[0]
        assert 'lastName' in children[0]
        assert 'birthDate' in children[0]
        assert 'awakeAvatarUrl' in children[0]
