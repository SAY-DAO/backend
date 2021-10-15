from tests.helper import BaseTestClass


CART_URL = '/api/v2/mycart'


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
