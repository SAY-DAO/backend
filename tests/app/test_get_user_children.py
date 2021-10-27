from tests.helper import BaseTestClass


USER_CHILDREN_URL = '/api/v2/user/children/userId=%s'


class TestUserChildren(BaseTestClass):
    def mockup(self):
        self.user = self._create_random_user()
        self.child1 = self._create_random_child(
            isDeleted=False,
            isConfirmed=True,
            existence_status=1,
        )
        self._create_user_family(user=self.user, family=self.child1.family)

        self.child2 = self._create_random_child(
            isDeleted=False,
            isConfirmed=True,
            existence_status=1,
        )

    def test_get_user_children(self):
        res = self.client.get(USER_CHILDREN_URL % self.user.id)
        assert res.status_code == 401

        self.login(self.user)
        res = self.client.get(USER_CHILDREN_URL % -1)
        assert res.status_code == 403

        res = self.client.get(USER_CHILDREN_URL % 'me')
        assert res.status_code == 200
        assert 'children' in res.json
        assert isinstance(res.json['children'], list)
        assert len(res.json['children']) == 1
