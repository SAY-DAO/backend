import secrets

from sqlalchemy_utils import PhoneNumberType, EmailType

from . import *
from say.content import content
from say.render_template_i18n import render_template_i18n


"""
Verify Model
"""


def generate_6_digit_secret():
    return secrets.SystemRandom().randint(1000 * 100, 1000 * 1000 -1)


class Verification(base, Timestamp):
    __tablename__ = "verification"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    _code = Column(Unicode(6), nullable=False, default=generate_6_digit_secret)
    expire_at = Column(DateTime, nullable=False)
    type = Column(Unicode(10), nullable=False)
    verified = Column(Boolean, default=False, nullable=False)

    __mapper_args__ = {
        'polymorphic_on': type,
    }

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expire_at 


class PhoneVerification(Verification):
    phone_number = Column(PhoneNumberType(), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'phone',
    }

    def send(self):
        from say.tasks import send_sms

        send_sms.delay(
            self.phone_number.e164,
            content['CONFIRM_PHONE'] % self._code,
        )


class EmailVerification(Verification):

    email = Column(EmailType, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'email',
    }

    def send(self):
        from say.tasks import send_embeded_subject_email

        send_embeded_subject_email.delay(
            to=self.email,
            html=render_template_i18n(
                'email_verification.html',
                code=str(self._code),
                locale=get_locale(),
            ),
        )


