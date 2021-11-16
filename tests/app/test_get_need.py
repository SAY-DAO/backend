from random import choice

from tests.helper import BaseTestClass


NEED_URL = '/api/v2/need/needId=%s'


class TestNeed(BaseTestClass):
    def mockup(self):
        self.payment = self._create_payment()
        self.user = self.payment.user
        self.need = self.payment.need
        self._create_user_family(user=self.user, family=self.need.child.family)

    def test_get_needs(self):
        self.login(self.user)

        res = self.client.get(
            NEED_URL % self.need.id,
        )
        assert res.status_code == 200
        assert isinstance(res.json['participants'], list)
        assert len(res.json['participants']) == 1
        assert res.json['participants'][0]['id_user'] == self.user.id
        assert res.json['participants'][0]['username'] == self.user.userName
        assert res.json['participants'][0]['user_avatar'] == self.user.avatarUrl
