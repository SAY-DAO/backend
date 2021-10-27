from datetime import datetime

import ujson

from say.roles import ADMIN
from say.roles import NGO_SUPERVISOR
from say.roles import SAY_SUPERVISOR
from say.roles import SOCIAL_WORKER
from say.roles import SUPER_ADMIN
from tests.helper import BaseTestClass


ADD_NEED_URL = '/api/v2/need/'


class TestAddNeed(BaseTestClass):
    def mockup(self):
        self.child = self._create_random_child(
            isConfirmed=True,
            isDeleted=False,
            isMigrated=False,
        )

    def test_add_need(self):
        self.login_sw(self.child.social_worker)
        data = dict(
            child_id=self.child.id,
            category=0,
            cost='123,000',
            name_translations=ujson.dumps(dict(fa='fa name')),
            description_translations=ujson.dumps(dict(fa='fa desc')),
            type=0,
            isUrgent=False,
            imageUrl=self.create_test_file('imageUrl.jpg'),
        )

        res = self.client.post(
            ADD_NEED_URL,
            content_type='multipart/form-data',
            data=data,
        )
        assert res.status_code == 200
        # TODO: Add more tests