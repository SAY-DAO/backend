from random import choice

from say.models.need_status_update import NeedStatusUpdate
from tests.helper import BaseTestClass


NEED_URL = '/api/v2/needs'


class TestNeed(BaseTestClass):
    def _test_filtering(self, field, data, db_column=None):
        db_column = db_column or field
        values = set(map(lambda n: getattr(n, db_column), data))
        for v in values:
            res = self.client.get(NEED_URL, query_string={field: v})
            assert res.status_code == 200
            assert res.json['totalCount'] == len(
                [*filter(lambda n: getattr(n, db_column) == v, data)]
            )

    def mockup(self):
        self.sw = self._create_random_sw()

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
        self._test_filtering('created_by', needs, 'created_by_id')
        self._test_filtering('confirmed_by', needs, 'confirmUser')

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

        # Test purchased_by
        sw = self._create_random_sw()
        other_sw = self._create_random_sw()
        self.session.add(
            NeedStatusUpdate(need=needs[0], sw=sw, new_status=3, old_status=2)
        )
        self.session.add(
            NeedStatusUpdate(need=needs[1], sw=sw, new_status=3, old_status=2)
        )
        self.session.add(
            NeedStatusUpdate(need=needs[5], sw=sw, new_status=3, old_status=2)
        )
        self.session.add(
            NeedStatusUpdate(need=needs[5], sw=sw, new_status=3, old_status=4)
        )
        self.session.add(
            NeedStatusUpdate(need=needs[0], sw=sw, new_status=3, old_status=2)
        )
        self.session.add(
            NeedStatusUpdate(need=needs[0], sw=other_sw, new_status=3, old_status=2)
        )
        self.session.add(
            NeedStatusUpdate(need=needs[2], sw=other_sw, new_status=3, old_status=2)
        )
        self.session.add(
            NeedStatusUpdate(need=needs[3], sw=sw, new_status=2, old_status=3)
        )

        self.session.commit()

        res = self.client.get(
            NEED_URL,
            query_string=dict(
                purchased_by=sw.id,
            ),
        )
        assert res.status_code == 200
        assert res.json['totalCount'] == 3
        assert set(n['id'] for n in res.json['needs']) == {
            needs[0].id,
            needs[1].id,
            needs[5].id,
        }
