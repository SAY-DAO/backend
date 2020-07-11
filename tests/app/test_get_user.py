from datetime import datetime

from say.models import User
from tests.helper import ApplicableTestCase


class TestGetUser(ApplicableTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.password = '123456'
        u = User(
            userName='test',
            emailAddress='test@test.com',
            phone_number='+989990009900',
            password=cls.password,
            firstName='test',
            lastName='test',
            city=1,
            country=1,
            lastLogin=datetime.utcnow(),
        )
        session.add(u)
        session.commit()
        cls.user = u

    def test_get(self):
        a = self.login(self.user.userName, self.password)
        # user = self.client.get('')
        assert self.user.id is not None
