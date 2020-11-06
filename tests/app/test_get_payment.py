from tests.helper import BaseTestClass

GET_PAYMENT_URL = '/api/v2/payment/id=%s'


class TestPayment(BaseTestClass):
    def mockup(self):
        self.password = '123456'
        self.user = self.create_user(self.password)

    def test_get_payment_not_admin_user(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}
        payment_id = ''
        res = self.client.get(
            GET_PAYMENT_URL % payment_id,
            headers=headers
        )
        assert res.status_code == 403

    def test_get_payment_wrong_need_id(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}
        payment_id = ''
        res = self.client.get(
            GET_PAYMENT_URL % payment_id,
            headers=headers
        )
        assert res.status_code == 404

    def test_get_payment(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}
        payment_id = ''
        res = self.client.get(
            GET_PAYMENT_URL % payment_id,
            headers=headers
        )
        assert res.status_code == 200