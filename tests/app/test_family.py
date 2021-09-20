import pytest
from flask.globals import session

from say.crud.search import calc_weights
from say.models import UserFamily
from tests.helper import BaseTestClass


FAMILY_V3_URL = '/api/v3/families/%s/join'


class TestJoinFamily(BaseTestClass):
    def mockup(self):
        self.url = FAMILY_V3_URL
        self.pw = '123456'
        self.user = self._create_random_user(password=self.pw)
        self.child = self._create_random_child(
            isDeleted=False, isConfirmed=True, existence_status=1
        )
        self.family = self.child.family

    def test_join_family(self):
        data = dict(role=0)
        res = self.client.post(self.url % self.child.family.id, data=data)
        assert res.status_code == 401

        self.login(self.user.userName, self.pw)

        res = self.client.post(self.url % self.child.family.id, data=data)
        assert res.status_code == 200

        res = self.client.post(self.url % self.child.family.id, data=data)
        assert res.status_code == 747

        # Back to previous role
        self.user.user_families[0].isDeleted = True
        self.session.save(self.user)
        data = dict(role=2)
        res = self.client.post(self.url % self.child.family.id, data=data)
        assert res.status_code == 746

    @pytest.mark.parametrize(
        'role,code', [(0, 744), (1, 744), (2, 200), (3, 200), (4, 200), (5, 200)]
    )
    def test_join_family_role_taken(self, role, code):
        data = dict(role=role)
        another_user = self._create_random_user(password=self.pw)
        self.login(another_user.userName, self.pw)
        res = self.client.post(self.url % self.child.family.id, data=data)
        assert res.status_code == 200

        self.login(self.user.userName, self.pw)
        res = self.client.post(self.url % self.child.family.id, data=data)
        assert res.status_code == code

    @pytest.mark.parametrize(
        'role,code', [(-1, 400), (1000, 400)]
    )
    def test_join_family_invalid_role(self, role, code):
        data = dict(role=role)
        self.login(self.user.userName, self.pw)
        res = self.client.post(self.url % self.child.family.id, data=data)
        assert res.status_code == code

    @pytest.mark.parametrize(
        'field,value,code', [
            ('isDeleted', True, 404),
            ('isConfirmed', False, 404),
            ('existence_status', 0, 404),
        ]
    )
    def test_join_family_child_conditions(self, field, value, code):
        setattr(self.child, field, value)
        self.session.save(self.child)

        data = dict(role=0)
        self.login(self.user.userName, self.pw)
        res = self.client.post(self.url % self.child.family.id, data=data)
        assert res.status_code == code
