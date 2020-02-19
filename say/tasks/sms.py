from say.api import sms_provider
from . import celery


@celery.task()
def send_sms(to, text):
    return sms_provider.send(to, text)

