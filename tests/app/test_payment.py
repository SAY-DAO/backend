import pytest

from say.api.ext import idpay
from say.api.payment_api import validate_amount
from say.config import configs
from say.exceptions import AmountTooHigh
from say.exceptions import AmountTooLow
from tests.helper import BaseTestClass


PAYMENT_V2_URL = '/api/v2/payment'


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
        self.user = self._create_random_user(password=self.pw)
        self.user_family = self._create_user_family(self.user, self.need.child.family)

    @staticmethod
    def _mocked_idpay_new_tx(**kwargs):
        return {
            'id': 'daf912385d155c0c414f199e67d025e9',
            'link': 'https://idpay.ir/p/ws-sandbox/abcd',
        }

    @staticmethod
    def _mocked_idpay_new_tx_error(**kwargs):
        return {
            'error_code': list(idpay.ERRORS.keys())[0],
        }

    def test_validate_amount(self):
        assert validate_amount(self.need, self.min_amount) == self.min_amount
        assert validate_amount(self.need, self.need.cost) == self.need.cost

        with pytest.raises(AmountTooLow):
            validate_amount(self.need, self.min_amount - 1)

        with pytest.raises(AmountTooLow):
            validate_amount(self.need, -1)

        with pytest.raises(AmountTooHigh):
            validate_amount(self.need, self.need.cost + 1)

    def test_add_payment(self, mocker):
        mocker.patch.object(
            idpay,
            'new_transaction',
            self._mocked_idpay_new_tx,
        )

        self.login(self.user.userName, self.pw)

        data = {
            'needId': self.need.id,
            'amount': self.need.cost,
            'useCredit': False,
        }

        res = self.client.post(
            PAYMENT_V2_URL,
            json=data,
        )
        assert res.status_code == 200
        assert res.json['link'] is not None

        # When amount missing
        res = self.client.post(
            PAYMENT_V2_URL,
            json={'needId': self.need.id},
        )
        assert res.status_code == 400

        # When need_id missing
        res = self.client.post(
            PAYMENT_V2_URL,
            json={'amount': self.user.id},
        )
        assert res.status_code == 400

        # When donation is zero
        res = self.client.post(
            PAYMENT_V2_URL,
            json={**data, 'donate': 0},
        )
        assert res.status_code == 200

        # When donation negative
        res = self.client.post(
            PAYMENT_V2_URL,
            json={**data, 'donate': -1},
        )
        assert res.status_code == 400

        # When donation invalid
        res = self.client.post(
            PAYMENT_V2_URL,
            json={**data, 'donate': 'invalid'},
        )
        assert res.status_code == 400

        # When amount invalid
        res = self.client.post(
            PAYMENT_V2_URL,
            json={**data, 'amount': 'invalid'},
        )
        assert res.status_code == 400

        # When amount negative
        res = self.client.post(
            PAYMENT_V2_URL,
            json={**data, 'amount': -1},
        )
        assert res.status_code == 400

        # Invalid need id
        res = self.client.post(
            PAYMENT_V2_URL,
            json={**data, 'needId': 'abc'},
        )
        assert res.status_code == 400

        # when idpay returns error
        mocker.patch.object(
            idpay,
            'new_transaction',
            self._mocked_idpay_new_tx_error,
        )
        res = self.client.post(PAYMENT_V2_URL, json=data)
        assert res.status_code == 422

    def test_add_payment_partial_need(self, mocker):
        mocker.patch.object(
            idpay,
            'new_transaction',
            self._mocked_idpay_new_tx,
        )

        self.login(self.user.userName, self.pw)

        p1 = self._create_payment(
            need=self.need,
            user=self.user,
            need_amount=self.need.cost / 2,
        )
        p1.verify()
        self.session.save(p1)

        data = {
            'needId': self.need.id,
            'amount': self.need.unpaid_cost,
        }

        res = self.client.post(
            PAYMENT_V2_URL,
            json=data,
        )
        assert res.status_code == 200

        res = self.client.post(
            PAYMENT_V2_URL,
            json={**data, 'amount': self.need.unpaid_cost + 1},
        )
        assert res.status_code == 422

    def test_add_payment_done_need(self, mocker):
        mocker.patch.object(
            idpay,
            'new_transaction',
            self._mocked_idpay_new_tx,
        )

        self.login(self.user.userName, self.pw)

        p1 = self._create_payment(
            need=self.need,
            user=self.user,
            need_amount=self.need.cost,
        )
        p1.verify()
        self.session.save(p1)

        data = {
            'needId': self.need.id,
            'amount': self.need.cost,
        }

        res = self.client.post(
            PAYMENT_V2_URL,
            json=data,
        )
        assert res.status_code == 422

    def test_add_payment_unconfirmed_need(self, mocker):
        mocker.patch.object(
            idpay,
            'new_transaction',
            self._mocked_idpay_new_tx,
        )

        self.login(self.user.userName, self.pw)
        self.need.unconfirm()
        self.session.save(self.need)

        data = {
            'needId': self.need.id,
            'amount': self.need.cost,
        }

        res = self.client.post(
            PAYMENT_V2_URL,
            json=data,
        )
        assert res.status_code == 422

    def test_add_payment_deleted_need(self, mocker):
        mocker.patch.object(
            idpay,
            'new_transaction',
            self._mocked_idpay_new_tx,
        )

        self.login(self.user.userName, self.pw)
        self.need.delete()
        self.session.save(self.need)

        data = {
            'needId': self.need.id,
            'amount': self.need.cost,
        }

        res = self.client.post(
            PAYMENT_V2_URL,
            json=data,
        )
        assert res.status_code == 400

    def test_add_payment_by_non_family_member(self, mocker):
        mocker.patch.object(
            idpay,
            'new_transaction',
            self._mocked_idpay_new_tx,
        )

        self.login(self.user.userName, self.pw)
        self.user_family.isDeleted = True
        self.session.save(self.user_family)

        data = {
            'needId': self.need.id,
            'amount': self.need.cost,
        }

        res = self.client.post(
            PAYMENT_V2_URL,
            json=data,
        )
        assert res.status_code == 422

    def test_add_payment_by_credit(self, mocker):
        mocker.patch.object(
            idpay,
            'new_transaction',
            self._mocked_idpay_new_tx,
        )

        self.login(self.user.userName, self.pw)

        credit_amount = self.need.cost / 2
        self.user.charge_wallet(credit_amount)
        self.session.save(self.user)

        data = {
            'needId': self.need.id,
            'amount': self.need.cost,
            'useCredit': True,
        }

        res = self.client.post(
            PAYMENT_V2_URL,
            json=data,
        )
        assert res.status_code == 200
        payment = res.json
        assert payment['link'] is not None
        assert payment['credit_amount'] == credit_amount
        assert payment['bank_amount'] == self.need.unpaid_cost - credit_amount

    def test_add_payment_by_credit_when_bank_amount_less_than_min_allowed(self, mocker):
        mocker.patch.object(
            idpay,
            'new_transaction',
            self._mocked_idpay_new_tx,
        )

        self.login(self.user.userName, self.pw)

        credit_amount = self.need.cost - configs.MIN_BANK_AMOUNT + 1
        self.user.charge_wallet(credit_amount)
        self.session.save(self.user)

        data = {
            'needId': self.need.id,
            'amount': self.need.cost,
            'useCredit': True,
        }

        res = self.client.post(
            PAYMENT_V2_URL,
            json=data,
        )
        assert res.status_code == 200
        payment = res.json
        assert payment['link'] is not None
        assert payment['credit_amount'] == self.need.unpaid_cost - configs.MIN_BANK_AMOUNT
        assert payment['bank_amount'] == configs.MIN_BANK_AMOUNT

    def test_full_payment_by_credit(self, mocker):
        mocker.patch.object(
            idpay,
            'new_transaction',
            self._mocked_idpay_new_tx,
        )

        self.login(self.user.userName, self.pw)

        credit_amount = self.need.cost * 3
        self.user.charge_wallet(credit_amount)
        self.session.save(self.user)

        data = {
            'needId': self.need.id,
            'amount': self.need.cost,
            'useCredit': True,
        }

        res = self.client.post(
            PAYMENT_V2_URL,
            json=data,
        )
        assert res.status_code == 299
        assert res.json['response'] is not None

        self.session.expire_all()
        assert self.user.credit == credit_amount - self.need.cost
        assert self.need.is_done is True
        assert self.need.unpaid_cost == 0
        assert self.need.status == 2
