import bs4 as bs
from flask_mail import Message

from say.api.ext import mail
from say.celery import celery


def get_subject_from_html(html):
    """
    Extract subject (title) from rendered html of email

    <title ...> some title </title>
    """
    soup = bs.BeautifulSoup(html)
    subject_element = soup.find('title')
    return subject_element.text


@celery.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_kwargs={'max_retries': 80},
)
def send_email(subject, to, html, cc=[], bcc=[]):
    if isinstance(to, str):
        to = [to]

    if isinstance(cc, str):
        cc = [cc]

    email = Message(
        subject=subject,
        recipients=to,
        html=html,
        cc=cc,
        bcc=bcc,
    )
    mail.send(email)


@celery.task
def send_embeded_subject_email(to, html, cc=[], bcc=[]):
    subject = get_subject_from_html(html).strip()
    return send_email.delay(subject, to, html, cc, bcc)
