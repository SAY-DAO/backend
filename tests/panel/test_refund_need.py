from datetime import datetime

import pytest

from tests.helper import BaseTestClass


class TestRefundNeed(BaseTestClass):
    @pytest.mark.parametrize(
        'type',
        [0, 1],
    )
    def test_refund_need(self, type):
        self.need = self._create_random_need(
            cost=3000,
            status=2,
            type=type,
        )

        self.p1 = self._create_payment(
            need=self.need,
            need_amount=1000,
            verified=datetime.utcnow(),
        )

        self.p2 = self._create_payment(
            need=self.need,
            need_amount=2000,
            verified=datetime.utcnow(),
        )

        new_cost = 1000
        refunds = self.need.refund_extra_credit(new_cost)
        self.session.expire(self.need)
        assert self.need.paid == new_cost
        assert refunds is not None
        assert len(refunds) == 2
        for r in refunds:
            assert -r.need_amount in [
                667,
                1333,
            ]

        for need_family in self.need.participants:
            assert need_family.paid in [
                333,
                667,
            ]
