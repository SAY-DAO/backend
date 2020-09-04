from say.models import ResetPassword, User
from say.orm import session
from tests.app.test_reset_password import RESET_PASS_PHONE_URL
from tests.helper import BaseTestClass

CONFIRM_RESET_PASS_URL = '/api/v2/auth/password/reset/confirm/token=%s'


class TestConfirmResetPass(BaseTestClass):
    def mockup(self):
        self.password = '123456'
        self.user = self.create_user(self.password)

    def test_confirm_reset_pass(self):

        # reset_pass_res = self.client.post(
        #     RESET_PASS_PHONE_URL,
        #     data={
        #         'phoneNumber': '+989127616539'
        #     }
        # )

        user = session.query(User) \
            .filter_by(phone_number='+989127616539') \
            .filter_by(is_phonenumber_verified=True) \
            .first()

        if user:
            reset_password = ResetPassword(user=user)
            session.add(reset_password)
            session.flush()


        #assert reset_pass_res.status_code == 200

        reset_password = session.query(ResetPassword) \
            .filter_by(user_id=self.user.id) \
            .filter(ResetPassword.is_used == False) \
            .filter(ResetPassword.is_expired == False) \
            .first()

        print(self.user.id)
        assert reset_password is not None

        print(reset_password.token)

        res = self.client.post(
            CONFIRM_RESET_PASS_URL % reset_password.token,
            data={
                'password': '123789',
                'confirm_password': '123789'
            }
        )
        print(res.json['message'])
        assert res.status_code == 200
