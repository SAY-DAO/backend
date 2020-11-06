from tests.helper import BaseTestClass

GET_ALL_PAYMENT_URL = '/api/v2/payment/all'


class TestPayment(BaseTestClass):
    def mockup(self):
        self.password = '123456'
        self.user = self.create_user(self.password)

    def test_get_all_payments_not_admin_user(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}
        res = self.client.get(
            GET_ALL_PAYMENT_URL,
            query_string={'need_id': '2', 'take': 10, 'skip': 0},
            headers=headers
        )
        assert res.status_code == 403

    def test_get_all_payments_wrong_need_id(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}
        res = self.client.get(
            GET_ALL_PAYMENT_URL,
            query_string={'need_id': '2', 'take': 10, 'skip': 0},
            headers=headers
        )
        assert res.status_code == 404

    def test_get_all_payments(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}
        res = self.client.get(
            GET_ALL_PAYMENT_URL,
            query_string={'need_id': '2', 'take': 10, 'skip': 0},
            headers=headers
        )
        assert res.status_code == 200
