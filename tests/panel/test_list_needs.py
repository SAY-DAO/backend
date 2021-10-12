from datetime import datetime

from sqlalchemy.orm import query

from tests.helper import BaseTestClass


LIST_NEEDS_URL = '/api/v2/needs'


class TestListNeeds(BaseTestClass):
    def mockup(self):
        self.password = 'password'
        self.user = self.create_panel_user(password=self.password)
        self.needs = []

        for _ in range(5):
            need = self._create_random_need()
            self._create_need_receipt(need=need)
            self._create_need_receipt(need=need)
            self._create_need_receipt(need=need, deleted=datetime.utcnow())
            self.needs.append(need)

    def test_list_needs(self):
        self.login_sw(self.user.userName, self.password)

        res = self.client.get(
            LIST_NEEDS_URL,
        )
        assert res.status_code == 200
        needs = res.json['needs']
        assert len(needs) == len(self.needs)
        assert needs[0]['receipt_count'] == 2

    def test_list_needs_filtering(self):
        self.login_sw(self.user.userName, self.password)

        res = self.client.get(
            LIST_NEEDS_URL,
            query_string=dict(is_confirmed=True),
        )
        assert res.status_code == 200
        assert len(res.json['needs']) == len(
            list(filter(lambda n: n.isConfirmed is True, self.needs))
        )

        res = self.client.get(
            LIST_NEEDS_URL,
            query_string=dict(is_confirmed=False),
        )
        assert res.status_code == 200
        assert len(res.json['needs']) == len(
            list(filter(lambda n: n.isConfirmed is False, self.needs))
        )
