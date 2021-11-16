from random import choice

from tests.helper import BaseTestClass


NEED_URL = '/api/v2/needs'


class TestNeed(BaseTestClass):
    def _test_filtering(self, field, data):
        values = set(map(lambda n: getattr(n, field), data))
        for v in values:
            res = self.client.get(NEED_URL, query_string={field: v})
            assert res.status_code == 200
            assert res.json['totalCount'] == len(
                [*filter(lambda n: getattr(n, field) == v, data)]
            )

    def mockup(self):
        self.sw = self.create_panel_user()

    def test_get_needs(self):
        self.login_sw(self.sw)

        needs = [
            self._create_random_need(
                isDeleted=False,
                isConfirmed=choice([True, False]),
                status=choice(range(4)),
                is_reported=choice([True, False]),
                type=choice([0, 1]),
            )
            for i in range(10)
        ]

        res = self.client.get(
            NEED_URL,
        )
        assert res.status_code == 200
        assert res.json['totalCount'] == len(needs)

        self._test_filtering('isConfirmed', needs)
        self._test_filtering('isDone', needs)
        self._test_filtering('status', needs)
        self._test_filtering('is_reported', needs)
        self._test_filtering('type', needs)

        need = needs[0]
        ngo_id = need.child.id_ngo
        res = self.client.get(NEED_URL, query_string=dict(ngoId=ngo_id))
        assert res.status_code == 200
        assert res.json['totalCount'] == len(
            [*filter(lambda n: n.child.id_ngo == ngo_id, needs)]
        )

        res = self.client.get(NEED_URL, query_string=dict(isChildConfirmed=True))
        assert res.status_code == 200
        assert res.json['totalCount'] == len(
            [*filter(lambda n: n.child.isConfirmed is True, needs)]
        )

        res = self.client.get(NEED_URL, query_string=dict(isChildConfirmed='abdc'))
        assert res.status_code == 400

        res = self.client.get(
            NEED_URL,
            query_string=dict(
                isChildConfirmed=need.child.isConfirmed,
                ngoId=need.child.id_ngo,
            ),
        )
        assert res.status_code == 200
        assert res.json['totalCount'] == len(
            [
                *filter(
                    lambda n: n.child.isConfirmed is need.child.isConfirmed
                    and n.child.id_ngo == need.child.id_ngo,
                    needs,
                )
            ]
        )
