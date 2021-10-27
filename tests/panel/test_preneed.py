import pytest

from say.constants import DEFAULT_CHILD_ID
from say.crud.search import calc_weights
from say.models import UserFamily
from tests.helper import BaseTestClass


PRENEED_V2_URL = '/api/v2/preneeds/'


class TestPreNeed(BaseTestClass):
    def mockup(self):
        self.child = self._create_random_child(
            id=DEFAULT_CHILD_ID,
            isDeleted=False,
            isConfirmed=True,
            existence_status=1,
        )
        self.need = self._create_random_need(
            isDeleted=False,
            isConfirmed=True,
            status=0,
            type=1,
            child=self.child,
        )

        self.sw = self._create_random_sw()

    @pytest.mark.parametrize('url', [PRENEED_V2_URL])
    def test_list_preneed(self, url):
        res = self.client.get(url)
        assert res.status_code == 401

        self.login_sw(self.sw)
        res = self.client.get(url)
        assert res.status_code == 200
        assert len(res.json) == len(self.child.needs)
