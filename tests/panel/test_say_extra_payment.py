from datetime import datetime

import pytest

from say.constants import SAY_USER
from tests.helper import BaseTestClass


class TestSayExtraPayment(BaseTestClass):
    @pytest.mark.parametrize(
        'type',
        [0, 1],
    )
    def test_say_extra_payment(self, type):
        self._create_say_user()
        self.need = self._create_random_need(
            cost=3000,
            purchase_cost=4000,
            status=2,
            type=type,
        )

        self.p1 = self._create_payment(
            need=self.need,
            need_amount=3000,
            verified=datetime.utcnow(),
        )

        say_payment = self.need.say_extra_payment()
        self.session.expire(self.need)
        assert self.need.paid == self.need.purchase_cost
        assert say_payment.need_amount == 1000
