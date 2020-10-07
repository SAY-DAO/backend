from say.api import sms_provider
from say.celery import celery


@celery.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=30,
    retry_kwargs={'max_retries': 6},
)
def send_sms(to, text):
    return sms_provider.send(to, text)
