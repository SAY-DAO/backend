from flask_mail import Message
import bs4 as bs

from . import celery
from say.api import mail


'''
Extract subject (a p tag with id = 'subject') from rendered html of email

<p id='subject' ...> some sobject {somechild.name} </p>
'''
def get_subject_from_html(html):
    soup = bs.BeautifulSoup(html)
    subject_element = soup.find('p', attrs={'id': 'subject'})
    return subject_element.text


@celery.task()
def send_email(subject, to, html, cc=[], bcc=[]):
    if isinstance(to, str):
        to = [to]

    email = Message(
        subject=subject,
        recipients=to,
        html=html,
        cc=cc,
        bcc=bcc,
    )
    mail.send(email)


@celery.task()
def send_embeded_subject_email(to, html, cc=[], bcc=[]):
    subject = get_subject_from_html(html).strip()
    if isinstance(to, str):
        to = [to]

    email = Message(
        subject=subject,
        recipients=to,
        html=html,
        cc=cc,
        bcc=bcc,
    )
    mail.send(email)
