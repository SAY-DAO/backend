import secrets
from datetime import datetime
from urllib.parse import urljoin

from say.api import app
from say.render_template_i18n import render_template_i18n
from say.tasks import send_embeded_subject_email, send_sms
from say.locale import ChangeLocaleTo
from say.content import content

from . import *

"""
Reset Password Model
"""


def expire_at():
    return datetime.utcnow() \
        + timedelta(seconds=app.config['RESET_PASSWORD_EXPIRE_TIME'])


class ResetPassword(base):
    __tablename__ = "reset_password"

    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    token = Column(
        String,
        nullable=False,
        default=lambda: secrets.token_urlsafe(
            app.config['RESET_PASSWORD_TOKEN_LENGTH']
        ),
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
            app.config['BASE_URL'],
            app.config['SET_PASSWORD_URL'] + f'?token={self.token}'
        )

    def send_email(self, language):
        return send_embeded_subject_email.delay(
            to=self.user.emailAddress,
            html=render_template_i18n(
                'reset_password.html',
                user=self.user,
                link=self.link,
                locale=language,
            )
        )

    def send_sms(self, language):
        with ChangeLocaleTo(language):
            send_sms.delay(
                self.user.phone_number.e164,
                content['RESET_PASSWORD'] % self.link
            )

