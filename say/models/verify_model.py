import secrets

from sqlalchemy import DateTime
from sqlalchemy_utils import PhoneNumberType, EmailType

from . import *
from say.content import content
from say.tasks import send_embeded_subject_email, send_sms


def generate_6_digit_secret():
    return secrets.SystemRandom().randint(1000 * 100, 1000 * 1000 -1)


"""
Verify Model
"""


class Verification(base, Timestamp):
    __tablename__ = "verification"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    _code = Column(Unicode(6), nullable=False, default=generate_6_digit_secret)
    expire_at = Column(DateTime, nullable=False)
    type = Column(Unicode(10), nullable=False)

    __mapper_args__ = {
        'polymorphic_on': type,
    }


class PhoneVerification(Verification):
    phone_number = Column(PhoneNumberType(), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'phone',
    }

    def send(self):
        send_sms.delay(
            self.phone_number.e164,
            content['CONFIRM_PHONE'] % self._code,
        )


class EmailVerification(Verification):
    email = Column(EmailType, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'email',
    }

    def send_verify_email(self):
        send_embeded_subject_email.delay(
            to=self.email,
            html=render_template_i18n(
                'email_verification.html',
                code=self._code,
                locale=get_locale(),
            ),
        )


