from say.roles import ADMIN
from say.roles import ROLES
from say.roles import SAY_SUPERVISOR
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


DELETE_SW_URL = '/api/v2/socialworkers/%s'


class TestDeleteSocialWorker(BaseTestClass):
    def test_delete_social_worker(self):
        self.login_as_sw(role=SUPER_ADMIN)
        sw = self._create_random_sw(is_deleted=False)
        self._create_random_child(
            sw=sw,
            isConfirmed=False,
        ),

        res = self.client.delete(
            DELETE_SW_URL % sw.id,
        )

        self.assert_ok(res)
        assert res.json['isDeleted'] is True

        # Delete again
        res = self.client.delete(
            DELETE_SW_URL % sw.id,
        )

        self.assert_code(res, 404)

        # Invalid id
        res = self.client.delete(
            DELETE_SW_URL % '0',
        )
        self.assert_code(res, 404)

        sw_with_active_child = self._create_random_sw(is_active=True)
        self._create_random_child(
            sw=sw_with_active_child,
            isConfirmed=True,
            isDeleted=False,
            isMigrated=False,
        ),
        res = self.client.delete(
            DELETE_SW_URL % sw_with_active_child.id,
        )
        self.assert_code(res, 400)

        for role in ROLES - {SUPER_ADMIN, SAY_SUPERVISOR, ADMIN}:
            self.login_as_sw(role=role)
            res = self.client.delete(
                DELETE_SW_URL % sw.id,
            )
            self.assert_code(res, 403)
