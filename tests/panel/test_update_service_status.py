from say.models.need_status_update import NeedStatusUpdate
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


UPDATE_NEED_URL = '/api/v2/need/update/needId=%s'


class TestUpdateServiceStatus(BaseTestClass):
    def mockup(self):
        self._create_say_user()

        self.need_with_receipt = self._create_random_need(
            type=0,
            status=3,
            isDeleted=False,
            isReported=True,
        )
        self._create_need_receipt(need=self.need_with_receipt)

        self.need_without_receipt = self._create_random_need(
            type=0,
            status=3,
            isDeleted=False,
            isReported=True,
        )

    def test_update_service_status_to_delivered(self):
        sw = self.login_as_sw(role=SUPER_ADMIN)
        data = dict(
            status=4,
        )

        # when need does not has any receipt
        res = self.client.patch(
            UPDATE_NEED_URL % self.need_without_receipt.id,
            data=data,
        )
        self.assert_code(res, 400)

        # when need has atleast one receipt
        res = self.client.patch(
            UPDATE_NEED_URL % self.need_with_receipt.id,
            data=data,
        )
        self.assert_ok(res)
        nsu = (
            self.session.query(NeedStatusUpdate)
            .filter(NeedStatusUpdate.need_id == res.json['id'])
            .one_or_none()
        )

        assert nsu is not None
        assert nsu.sw_id == sw.id
        assert nsu.old_status == 3
        assert nsu.new_status == 4
