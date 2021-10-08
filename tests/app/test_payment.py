import pytest

from say.api.payment_api import validate_amount
from say.config import configs
from say.exceptions import AmountTooHigh
from say.exceptions import AmountTooLow
from tests.helper import BaseTestClass


PAYMENT_V2_URL = '/api/v2/payment/'


class TestPayment(BaseTestClass):
    def mockup(self):
        self.min_amount = configs.MIN_BANK_AMOUNT
        self.pw = '123456'
        self.need = self._create_random_need(
            isDeleted=False,
            isConfirmed=True,
            status=0,
            type=1,
            cost=configs.MIN_BANK_AMOUNT * 10,
        )

        self.sw = self._create_random_sw(password=self.pw)

    def test_validate_amount(self):
        assert validate_amount(self.need, self.min_amount) == self.min_amount
        assert validate_amount(self.need, self.need.cost) == self.need.cost

        with pytest.raises(AmountTooLow):
            validate_amount(self.need, self.min_amount - 1)

        with pytest.raises(AmountTooLow):
            validate_amount(self.need, -1)

        with pytest.raises(AmountTooHigh):
            validate_amount(self.need, self.need.cost + 1)
