from datetime import datetime

from say.roles import ADMIN
from say.roles import SAY_SUPERVISOR
from say.roles import SOCIAL_WORKER
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


LIST_NEEDS_URL = '/api/v2/needs'
RECEIPT_URL = '/api/v2/receipts/'


class TestNeedReceipts(BaseTestClass):
    def mockup(self):
        self.sw = self.create_panel_user()

        self.need = self._create_random_need()
        self.r1 = self._create_need_receipt(need=self.need)
        self.public_receipt = self._create_need_receipt(
            need=self.need,
            receipt=self._create_random_receipt(is_public=True),
        )
        self.deleted_receipt = self._create_need_receipt(
            need=self.need,
            deleted=datetime.utcnow(),
        )

    def test_receipts_count(self):
        self.login_sw(self.sw)

        res = self.client.get(
            LIST_NEEDS_URL,
        )
        assert res.status_code == 200
        needs = res.json['needs']
        assert needs[0]['receipt_count'] == 2

    def test_get_public_receipt(self):
        res = self.client.get(
            RECEIPT_URL + str(self.public_receipt.id),
        )
        assert res.status_code == 200
        assert res.json['ownerId'] is None

        self.login_as_user()
        res = self.client.get(
            RECEIPT_URL + str(self.public_receipt.id),
        )
        assert res.status_code == 200
        assert res.json['ownerId'] is None

        for role in [SAY_SUPERVISOR, ADMIN, SUPER_ADMIN]:
            self.login_as(role)
            res = self.client.get(
                RECEIPT_URL + str(self.public_receipt.id),
            )
            assert res.status_code == 200
            assert res.json['ownerId'] is not None

        # Social workers only can see their receipts
        # (their child, or as NGO supervisio children of their ngo)
        self.login_as(SOCIAL_WORKER)
        res = self.client.get(
            RECEIPT_URL + str(self.public_receipt.id),
        )
        assert res.status_code == 404

    def test_get_receipt(self):
        self.login_as(SUPER_ADMIN)

        res = self.client.get(
            RECEIPT_URL + str(self.r1.id),
        )
        assert res.status_code == 200
        assert res.json['id'] == self.r1.id

        res = self.client.get(
            RECEIPT_URL + str(self.deleted_receipt),
        )
        assert res.status_code == 404

        # self.
        # receipt = self._create_need_receipt(
        #     need=self.need,
        #     receipt=self._create_random_receipt(is_public=True),
        # )
