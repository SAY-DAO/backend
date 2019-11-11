from flask_mail import Message

from say.api import celery, mail


@celery.task()
def send_email(subject, email, html):

    if type(email) is str:
        email = [email]

    email = Message(
        subject=subject,
        recipients=email,
        html=html,
    )
    mail.send(email)


