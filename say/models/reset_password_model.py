import secrets
from datetime import datetime
from urllib.parse import urljoin

from say.api import render_template, app
from say.tasks import send_embeded_subject_email

from . import *

"""
Reset Password Model
"""

def expire_at():
    return datetime.utcnow() \
        + timedelta(seconds=app.config['RESET_PASSSWORD_EXPIRE_TIME'])


class ResetPassword(base):
    __tablename__ = "reset_password"

    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    token = Column(String, nullable=False, default=secrets.token_urlsafe)
    expire_at = Column(DateTime, default=expire_at, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)

    user = relationship('UserModel', foreign_keys=user_id, uselist=False)

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
            html=render_template(
                'reset_password.html',
                user=self.user,
                link=self.link,
                locale=language,
            )
        )

