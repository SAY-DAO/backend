from datetime import datetime

from say.constants import SAY_USER
from tests.helper import BaseTestClass


class TestSayExtraPayment(BaseTestClass):
    def mockup(self):
        self._create_random_user(userName=SAY_USER)

        self.need = self._create_random_need(
            cost=3000,
            purchase_cost=4000,
            status=2,
        )

        self.p1 = self._create_payment(
            need=self.need,
            need_amount=3000,
            verified=datetime.utcnow(),
        )

    def test_say_extra_payment(self):
        say_payment = self.need.say_extra_payment()
        self.session.expire(self.need)
        assert self.need.paid == self.need.purchase_cost
        assert say_payment.need_amount == 1000
