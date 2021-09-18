from tests.helper import BaseTestClass


RANDOM_SEARCH_URL = '/api/v3/search/random'


class TestCart(BaseTestClass):
    def mockup(self):
        self.pw = '123456'
        self.user = self.create_user(password=self.pw)
        child = self._create_random_child(
            isDeleted=False, isConfirmed=True, existence_status=1
        )
        self._create_random_family(child)
        self._create_random_need(
            isDeleted=False,
            isConfirmed=True,
            status=0,
            type=1,
            child=child,
        )

    def test_get_cart(self):
        self.login(self.user.userName, self.pw)

        res = self.client.post(
            RANDOM_SEARCH_URL,
        )
        assert res.status_code == 200
        assert res.json['token'] is not None
        assert res.json['child'] is not None
