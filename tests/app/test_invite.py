from tests.helper import BaseTestClass


INVITE_URL = '/api/v3/invitations/'


class TestCart(BaseTestClass):
    def mockup(self):
        self.pw = '123456'
        self.user = self.create_user(password=self.pw)
        self.child = self._create_random_child(
            isDeleted=False, isConfirmed=True, existence_status=1
        )
        self._create_random_family(self.child)
        self._create_random_need(
            isDeleted=False,
            isConfirmed=True,
            status=0,
            type=1,
            child=self.child,
        )

    def test_get_cart(self):
        self.login(self.user.userName, self.pw)
        res = self.client.post(
            INVITE_URL,
            data=dict(
                familyId=self.child.familyId,
                role=0,
            )
        )
        assert res.status_code == 200
        assert res.json['token'] is not None
        assert res.json['child'] is not None
