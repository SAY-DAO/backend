from say.roles import ADMIN
from say.roles import ROLES
from say.roles import SAY_SUPERVISOR
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


ACTIVE_SW_URL = '/api/v2/socialworkers/%s/activate'


class TestActiveSocialWorker(BaseTestClass):
    def test_active_social_worker(self):
        self.login_as_sw(role=SUPER_ADMIN)
        sw = self._create_random_sw(isActive=False)

        res = self.client.post(
            ACTIVE_SW_URL % sw.id,
        )

        self.assert_ok(res)
        assert res.json['isActive'] is True

        # Activate again
        res = self.client.post(
            ACTIVE_SW_URL % sw.id,
        )

        self.assert_code(res, 400)

        # Invalid id
        res = self.client.post(
            ACTIVE_SW_URL % '0',
        )

        self.assert_code(res, 404)

        for role in ROLES - {SUPER_ADMIN, SAY_SUPERVISOR, ADMIN}:
            self.login_as_sw(role=role)
            res = self.client.post(
                ACTIVE_SW_URL % sw.id,
            )
            self.assert_code(res, 403)
