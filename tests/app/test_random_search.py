import pytest

from say.crud.search import calc_weights
from say.models import UserFamily
from tests.helper import BaseTestClass


RANDOM_SEARCH_V2_URL = '/api/v2/search/random'
RANDOM_SEARCH_V3_URL = '/api/v3/search/random'


class TestRandomSearch(BaseTestClass):
    def mockup(self):
        self.user = self._create_random_user()
        self.child = self._create_random_child(
            isDeleted=False, isConfirmed=True, existence_status=1
        )
        self.need = self._create_random_need(
            isDeleted=False,
            isConfirmed=True,
            status=0,
            type=1,
            child=self.child,
        )

        # For v2
        self._create_random_user(userName='say')

    @pytest.mark.parametrize('url', [RANDOM_SEARCH_V2_URL, RANDOM_SEARCH_V3_URL])
    def test_random_search(self, url):
        res = self.client.post(url)
        assert res.status_code == 200

        self.login(self.user)

        res = self.client.post(url)
        assert res.status_code == 200
        assert res.json['token'] is not None
        if url == RANDOM_SEARCH_V3_URL:
            assert res.json['child'] is not None
            assert len(res.json['child']['childFamilyMembers']) == 0

        # if child is deleted
        self.child.isDeleted = True
        self.session.save(self.child)
        res = self.client.post(url)
        assert res.status_code == 499

        # if child is unconfirmed
        self.child.isDeleted = False
        self.child.isConfirmed = False
        self.session.save(self.child)
        res = self.client.post(url)
        assert res.status_code == 499

        # if child is gone
        self.child.isConfirmed = True
        self.child.existence_status = 0
        self.session.save(self.child)
        res = self.client.post(url)
        assert res.status_code == 499

        # if child has no active needs
        self.child.existence_status = 1
        self.child.needs[0].isConfirmed = False
        self.session.save(self.child)
        res = self.client.post(url)
        assert res.status_code == 499

        self.child.needs[0].isConfirmed = True
        self.session.save(self.child)

        # In family of all children
        user_family = UserFamily(
            user=self.user,
            role=0,
            family=self.child.family,
        )
        self.session.save(user_family)
        res = self.client.post(url)
        assert res.status_code == 499

        # When leaved the family
        user_family.is_deleted = True
        self.session.save(user_family)
        res = self.client.post(url)
        assert res.status_code == 200

        # When user used to be father or mother but now it is taken
        another_user = self._create_random_user()
        another_user_family = UserFamily(
            family=self.child.family,
            user=another_user,
            role=0,
        )
        self.session.save(another_user_family)
        res = self.client.post(url)
        assert res.status_code == 499

        # When there is another child to adopt
        another_child = self._create_random_child(
            isDeleted=False, isConfirmed=True, existence_status=1
        )
        self._create_random_need(
            isDeleted=False,
            isConfirmed=True,
            status=0,
            type=1,
            child=another_child,
        )

        # Increase chance of prevoius child to be selected
        for _ in range(10):
            another_user = self._create_random_user()
            another_child.family.members.append(
                UserFamily(
                    family=self.child.family,
                    user=another_user,
                    role=2,
                )
            )

        self.session.save(another_child.family)

        res = self.client.post(url)
        assert res.status_code == 200
        if url == RANDOM_SEARCH_V3_URL:
            assert res.json['child'] is not None
            child = res.json['child']
            assert child['id'] == another_child.id
            assert child['childFamilyMembers'] is not None
            child_family_members = child['childFamilyMembers']
            assert len(child_family_members) == another_child.family.members_count
            assert child_family_members[0]['avatarUrl'] is not None
            assert child_family_members[0]['member_id'] is not None
            assert child_family_members[0]['role'] is not None

    @pytest.mark.parametrize(
        'user_children_count,expected', [(0, [1, 1, 1, 1]), (1, [1, 1, 1 / 2, 1 / 4])]
    )
    def test_calc_weights(self, user_children_count, expected):
        family_counts = [0, 0, 1, 3]
        factor = 1

        assert (
            calc_weights(
                family_counts=family_counts,
                user_children_count=user_children_count,
                factor=factor,
            )
            == expected
        )
