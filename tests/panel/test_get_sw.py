import pytest

from say.roles import ROLES
from say.roles import SAY_SUPERVISOR
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


GET_SW_URL = '/api/v2/socialWorker/socialWorkerId=%s'


class TestGetSocialWorker(BaseTestClass):
    def test_get_social_worker(self):
        admin = self.login_as_sw(role=SUPER_ADMIN)

        res = self.client.get(
            GET_SW_URL % admin.id,
        )
        from pudb import set_trace; set_trace()
        assert self.assert_ok(res)
        assert res.json['id'] == admin.id
        assert res.json['typeName'] == admin.privilege.name
        assert res.json['ngoName'] == admin.ngo.name
