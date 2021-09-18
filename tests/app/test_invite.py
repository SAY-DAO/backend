import pytest

from tests.helper import BaseTestClass


INVITE_V2_URL = '/api/v2/invitations/'
INVITE_V3_URL = '/api/v3/invitations/'


class TestInvite(BaseTestClass):
    def mockup(self):
        self.pw = '123456'
        self.user = self._create_random_user(password=self.pw)
        self.child = self._create_random_child(
            isDeleted=False, isConfirmed=True, existence_status=1
        )
        self._create_random_need(
            isDeleted=False,
            isConfirmed=True,
            status=0,
            type=1,
            child=self.child,
        )

    @pytest.mark.parametrize('url', [INVITE_V2_URL, INVITE_V3_URL])
    def test_post_invite(self, url):
        self.login(self.user.userName, self.pw)
        res = self.client.post(
            url,
            data=dict(
                familyId=self.child.familyId,
                role=0,
            )
        )
        assert res.status_code == 200
        assert res.json['token'] is not None
        if url == INVITE_V3_URL:
            assert res.json['child'] is not None
