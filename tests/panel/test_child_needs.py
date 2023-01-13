from random import choice

from say.models.need_status_update import NeedStatusUpdate
from tests.helper import BaseTestClass


CHILD_NEEDS_URL = '/api/v2/child/childId=%s/needs'


class TestNeed(BaseTestClass):
    def mockup(self):
        self.sw = self._create_random_sw()
        self.child = self._create_random_child(sw=self.sw)
        for _ in range(10):
            self._create_random_need(child=self.child)

    def test_child_needs(self):
        self.login_sw(self.sw)

        res = self.client.get(
            CHILD_NEEDS_URL % self.child.id,
        )
        assert res.status_code == 200
        assert res.json['needs'][0]['createdBy'] is not None
