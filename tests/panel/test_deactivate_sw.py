from say.roles import ADMIN
from say.roles import ROLES
from say.roles import SAY_SUPERVISOR
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


DEACTIVE_SW_URL = '/api/v2/socialworkers/%s/deactivate'


class TestDeactiveSocialWorker(BaseTestClass):
    def test_deactive_social_worker(self):
        self.login_as_sw(role=SUPER_ADMIN)
        sw = self._create_random_sw(isActive=True)
        self._create_random_child(
            sw=sw,
            isConfirmed=False,
        ),

        res = self.client.post(
            DEACTIVE_SW_URL % sw.id,
        )

        self.assert_ok(res)
        assert res.json['isActive'] is False

        # Deactivate again
        res = self.client.post(
            DEACTIVE_SW_URL % sw.id,
        )

        self.assert_code(res, 400)

        # Invalid id
        res = self.client.post(
            DEACTIVE_SW_URL % '0',
        )
        self.assert_code(res, 404)

        sw_with_active_child = self._create_random_sw(isActive=True)
        self._create_random_child(
            sw=sw_with_active_child,
            isConfirmed=True,
            isDeleted=False,
            isMigrated=False,
        ),
        res = self.client.post(
            DEACTIVE_SW_URL % sw_with_active_child.id,
        )
        self.assert_code(res, 400)

        for role in ROLES - {SUPER_ADMIN, SAY_SUPERVISOR, ADMIN}:
            self.login_as_sw(role=role)
            res = self.client.post(
                DEACTIVE_SW_URL % sw.id,
            )
            self.assert_code(res, 403)
