from say.roles import ADMIN
from say.roles import ROLES
from say.roles import SAY_SUPERVISOR
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


MIGRATE_SW_CHILDREN_URL = '/api/v2/socialWorker/%s/children/migrate'


class TestMigrateSocialWorkerChildren(BaseTestClass):
    def test_active_social_worker(self):
        self.login_as_sw(role=SUPER_ADMIN)
        sw = self._create_random_sw(isActive=True)
        new_sw = self._create_random_sw(isActive=True)
        self._create_random_child(sw, isDeleted=False)
        self._create_random_child(sw, isDeleted=False)
        self._create_random_child(sw, isDeleted=True)

        res = self.client.post(
            MIGRATE_SW_CHILDREN_URL % sw.id,
            data={'destinationSocialWorkerId': new_sw.id},
        )

        self.assert_ok(res)
        assert len(res.json) == 2
        assert res.json[0]['newSwId'] == new_sw.id
        assert res.json[0]['oldSwId'] == sw.id
        assert res.json[0]['migratedAt'] is not None
        assert res.json[0]['childId'] in [c.id for c in new_sw.children]
        assert res.json[0]['newGeneratedCode'].startswith(new_sw.generatedCode)
        assert res.json[0]['oldGeneratedCode'].startswith(sw.generatedCode)

        self.session.refresh(sw)
        assert sw.childCount == 1
        assert sw.currentChildCount == 0

        self.session.refresh(new_sw)
        assert new_sw.childCount == 2
        assert new_sw.currentChildCount == 2

        for role in ROLES - {SUPER_ADMIN, SAY_SUPERVISOR, ADMIN}:
            self.login_as_sw(role=role)
            res = self.client.post(
                MIGRATE_SW_CHILDREN_URL % sw.id,
                data={'destinationSocialWorkerId': new_sw.id},
            )

            self.assert_code(res, 403)

        self.login_as_sw(role=SUPER_ADMIN)
        res = self.client.post(
            MIGRATE_SW_CHILDREN_URL % sw.id,
            data={'destinationSocialWorkerId': sw.id},
        )

        self.assert_code(res, 400)

        deactive_sw = self._create_random_sw(is_active=False)
        res = self.client.post(
            MIGRATE_SW_CHILDREN_URL % sw.id,
            data={'destinationSocialWorkerId': deactive_sw.id},
        )

        self.assert_code(res, 400)

        res = self.client.post(
            MIGRATE_SW_CHILDREN_URL % deactive_sw.id,
            data={'destinationSocialWorkerId': sw.id},
        )

        self.assert_code(res, 404)

        deleted_sw = self._create_random_sw(is_active=False)
        res = self.client.post(
            MIGRATE_SW_CHILDREN_URL % sw.id,
            data={'destinationSocialWorkerId': deleted_sw.id},
        )

        self.assert_code(res, 400)

        res = self.client.post(
            MIGRATE_SW_CHILDREN_URL % deleted_sw.id,
            data={'destinationSocialWorkerId': sw.id},
        )

        self.assert_code(res, 404)
