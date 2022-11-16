from say.models import NeedStatusUpdate
from tests.helper import BaseTestClass


UPDATE_NEED_URL = '/api/v2/need/update/needId=%s'


class TestNeedStatusUpdate(BaseTestClass):
    def mockup(self):
        self.child = self._create_random_child(
            isConfirmed=True,
            isDeleted=False,
            isMigrated=False,
        )
        self.need = self._create_random_need(child=self.child, status=2)

    def test_create_need_status_update(self):
        self.login_sw(self.child.social_worker)
        data = dict(
            status=3,
        )

        res = self.client.patch(
            UPDATE_NEED_URL % self.need.id,
            content_type='multipart/form-data',
            data=data,
        )
        self.assert_ok(res)
        need_status_update = self.session.query(NeedStatusUpdate).filter(
            NeedStatusUpdate.need_id == self.need.id,
        ).one_or_none()

        assert need_status_update is not None
        assert need_status_update.old_status == 2
        assert need_status_update.new_status == 3
        assert need_status_update.sw_id == self.child.social_worker.id

