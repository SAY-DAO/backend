from tests.helper import BaseTestClass

DO_PAYMENT_URL = '/api/v2/payment'


class TestPayment(BaseTestClass):
    def mockup(self):
        self.password = '123456'
        self.user = self.create_user(self.password)

    def test_do_payment_wrong_need_id(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}

        res = self.client.post(
            DO_PAYMENT_URL,
            headers=headers,
            data={
                "needId": 0,
                "amount": 0,
                "donate": 0,
                "useCredit": False
            }
        )
        assert res.status_code == 404

    def test_do_payment(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}

        res = self.client.post(
            DO_PAYMENT_URL,
            headers=headers,
            data={
                "needId": 0,
                "amount": 0,
                "donate": 0,
                "useCredit": False
            }
        )
        assert res.status_code == 200

    def test_do_payment_not_enough_credit(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}

        res = self.client.post(
            DO_PAYMENT_URL,
            headers=headers,
            data={
                "needId": 0,
                "amount": 0,
                "donate": 0,
                "useCredit": True
            }
        )
        assert res.status_code == 400
