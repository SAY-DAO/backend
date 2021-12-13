from say.api.ext import idpay
from tests.helper import BaseTestClass


CART_URL = '/api/v2/mycart'
CART_PAYMENT_URL = CART_URL + '/payment'
CART_NEEDS_URL = CART_URL + '/needs'


class TestCart(BaseTestClass):
    def mockup(self):
        self.user = self._create_random_user()

    def test_get_cart(self):
        self.login(self.user)

        res = self.client.get(
            CART_URL,
        )
        assert res.status_code == 200
        assert res.json['id'] is not None

    def test_put_cart_invalid_input(self):
        self.login(self.user)

        res = self.client.put(
            CART_URL,
        )
        assert res.status_code == 400

    def test_put_cart(self):
        self.login(self.user)

        ok_needs = [
            self._create_random_need(self._create_user_family(self.user).family.child)
            for i in range(10)
        ]

        invalid_need_ids = [
            -1,  # invalid id
            self._create_random_need().id,  # need of another user or child
        ]
        ok_need_ids = [
            *map(lambda n: n.id, ok_needs),
        ]

        data = dict(needIds=[*invalid_need_ids, *ok_need_ids])
        res = self.client.put(
            CART_URL,
            json=data,
        )
        assert res.status_code == 600
        assert set(res.json['invalidNeedIds']) == set(invalid_need_ids)

        data = dict(needIds=ok_need_ids)
        res = self.client.put(
            CART_URL,
            json=data,
        )
        assert res.status_code == 200
        assert set([n['id'] for n in res.json['needs']]) == set(ok_need_ids)

    def test_add_need_to_cart(self):
        self.login(self.user)

        need = self._create_random_need(self._create_user_family(self.user).family.child)
        res = self.client.post(
            CART_NEEDS_URL,
            data=dict(needId=need.id),
        )
        assert res.status_code == 200

        # unpayable need
        unpayable_need = self._create_random_need()
        res = self.client.post(
            CART_NEEDS_URL,
            data=dict(needId=unpayable_need.id),
        )
        assert res.status_code == 400

    def test_delete_need_from_cart(self):
        self.login(self.user)

        cart_need = self._create_random_cart_need(cart=self.user.cart)
        res = self.client.delete(
            CART_NEEDS_URL,
            data=dict(needId=cart_need.need.id),
        )
        assert res.status_code == 200

        # need not in cart
        new_need = self._create_random_need()
        res = self.client.delete(
            CART_NEEDS_URL,
            data=dict(needId=new_need.id),
        )
        assert res.status_code == 404

        # invalid need id
        res = self.client.delete(
            CART_NEEDS_URL,
            data=dict(needId='not-int'),
        )
        assert res.status_code == 400

    def test_cart_payment(self, mocker):
        mocker.patch.object(
            idpay,
            'new_transaction',
            self._mocked_idpay_new_tx,
        )

        self.login(self.user)

        cart_need = self._create_random_cart_need(cart=self.user.cart)
        res = self.client.post(
            CART_PAYMENT_URL,
            data=dict(
                donation=1000,
                use_credit=False,
            ),
        )
        assert res.status_code == 200
        assert res.json['needsAmount'] == cart_need.need.cost
        assert res.json['donationAmount'] == 1000
        assert res.json['link'] is not None

    def test_cart_payment_empty(self, mocker):
        self.login(self.user)

        res = self.client.post(
            CART_PAYMENT_URL,
            data=dict(
                donation=1000,
                use_credit=False,
            ),
        )
        assert res.status_code == 600
