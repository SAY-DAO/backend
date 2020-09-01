from say.api import sms_provider
from . import celery


@celery.task(max_retries=5, autoretry_for=(Exception,), retry_backoff=2)
def send_sms(to, text):
    return sms_provider.send(to, text)
