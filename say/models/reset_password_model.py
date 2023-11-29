import secrets
from urllib.parse import urljoin

from say.content import content
from say.locale import ChangeLocaleTo
from say.render_template_i18n import render_template_i18n

from ..config import configs
from . import *


"""
Reset Password Model
"""


def expire_at():
    return datetime.utcnow() + timedelta(seconds=configs.RESET_PASSWORD_EXPIRE_TIME)


class ResetPassword(base):
    __tablename__ = "reset_password"

    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    token = Column(
        String,
        nullable=False,
        default=lambda: secrets.token_urlsafe(configs.RESET_PASSWORD_TOKEN_LENGTH),
        unique=True,
        index=True,
    )
    expire_at = Column(DateTime, default=expire_at, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)

    user = relationship('User', foreign_keys=user_id, uselist=False)

    @hybrid_property
    def is_expired(self):
        return self.expire_at < datetime.utcnow()

    @property
    def link(self):
        return urljoin(
            configs.BASE_URL, configs.SET_PASSWORD_URL + f'?token={self.token}'
        )

    def send_email(self, language):
        from say.tasks import send_embeded_subject_email

        return send_embeded_subject_email.delay(
            to=self.user.emailAddress,
            html=render_template_i18n(
                'reset_password.html',
                user=self.user,
                link=self.link,
                locale=language,
            ),
        )

    def send_sms(self, language):
        from say.tasks import send_sms

        with ChangeLocaleTo(language):
            send_sms.delay(
                self.user.phone_number.e164, content['RESET_PASSWORD'] % self.link
            )
