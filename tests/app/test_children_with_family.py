from tests.helper import BaseTestClass


CHILD_USER_GRAPH = '/api/v2/public/children'


class TestChildrenWithFamilyMembers(BaseTestClass):
    def test_get_needs(self):
        c1 = self._create_random_child(
            isDeleted=False,
            isMigrated=False,
            isConfirmed=True,
            existence_status=1,
        )

        u1 = self._create_random_user()
        u2 = self._create_random_user()
        self._create_user_family(family=c1.family, user=u1)
        self._create_user_family(family=c1.family, user=u2)

        n1 = self._create_random_need(child=c1)
        self._create_payment(need=n1, user=u1)

        res = self.client.get(CHILD_USER_GRAPH)
        self.assert_ok(res)

        children = res.json
        assert len(children) == 1
        assert 'id' in children[0]
        assert 'avatarUrl' in children[0]
        assert 'sayName' in children[0]
        assert 'family' in children[0]
        assert 'currentMembers' in children[0]['family']
        assert 'isParticipated' in children[0]['family']['currentMembers'][0]
        assert 'avatarUrl' in children[0]['family']['currentMembers'][0]
        assert 'username' in children[0]['family']['currentMembers'][0]
