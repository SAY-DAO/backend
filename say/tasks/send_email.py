from flask_mail import Message
import bs4 as bs

from . import celery
from say.api import mail


'''
Extract subject (title) from rendered html of email

<title ...> some title </title>
'''
def get_subject_from_html(html):
    soup = bs.BeautifulSoup(html)
    subject_element = soup.find('title')
    return subject_element.text


@celery.task(bind=True, max_retries=3)
def send_email(self, subject, to, html, cc=[], bcc=[]):
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
    try:
        mail.send(email)
    except:
        self.retry(countdown=3**self.request.retries)


@celery.task(bind=True, max_retries=3)
def send_embeded_subject_email(self, to, html, cc=[], bcc=[]):
    subject = get_subject_from_html(html).strip()

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
    try:
        mail.send(email)
    except:
        self.retry(countdown=3**self.request.retries)

