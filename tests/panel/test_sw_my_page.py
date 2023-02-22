import pytest

from say.roles import ADMIN
from say.roles import ROLES
from say.roles import SAY_SUPERVISOR
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


SW_MY_PAGE_URL = '/api/v2/socialworkers/my-page'


class TestSocialWorkerMyPage(BaseTestClass):
    def mockup(self):
        self.sw = self._create_random_sw()
        self.child1 = self._create_random_child(sw=self.sw, isDeleted=False, existence_status=1)
        n1 = self._create_random_need(child=self.child1)

        self._create_need_receipt(n1)
        self._create_need_receipt(n1)

        self._create_payment(n1)

        self._create_random_need_status_update(n1)

    def test_social_worker_my_page(self):
        self.login_sw(self.sw)
        res = self.client.get(
            SW_MY_PAGE_URL,
        )

        self.assert_code(res, 200)
        assert res.json['count'] == 1
        children = res.json['result']
        assert 'id' in children[0]
        assert 'sayName' in children[0]
        assert 'firstName' in children[0]
        assert 'lastName' in children[0]
        assert 'birthDate' in children[0]
        assert 'awakeAvatarUrl' in children[0]

        needs = children[0]['needs']
        assert needs is not None
        need = needs[0]
        assert sorted(
            [
                'id',
                'createdById',
                'name',
                'title',
                'imageUrl',
                'category',
                'type',
                'isUrgent',
                'link',
                'affiliateLinkUrl',
                'doingDuration',
                'img',
                'paid',
                'purchaseCost',
                'cost',
                'unpayable',
                'isDone',
                'isConfirmed',
                'unpayableFrom',
                'created',
                'updated',
                'confirmDate',
                'statusUpdates',
                'receipts_',
                'verifiedPayments',
                'confirmedBy',
                'status',
                'doneAt',
                'ngoDeliveryDate',
                'purchaseDate',
                'childDeliveryDate',
                'bankTrackId',
                'expectedDeliveryDate',
            ]
        ) == sorted(list(need.keys()))

        assert need['id']
        assert need['createdById']
        assert need['receipts_']
        assert need['statusUpdates']
        assert need['verifiedPayments']
