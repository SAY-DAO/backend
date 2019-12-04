from flask_mail import Message

from . import celery
from say.api import mail


@celery.task()
def send_email(subject, emails, html, cc=[], bcc=[]):

    if type(emails) is str:
        emails = [emails]

    email = Message(
        subject=subject,
        recipients=emails,
        html=html,
        cc=cc,
        bcc=bcc,
    )
    mail.send(email)


