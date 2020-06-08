from say.api import sms_provider
from . import celery


@celery.task(bind=True, max_retires=4)
def send_sms(to, text):
    try:
        return sms_provider.send(to, text)
    except:
        self.retry(countdown=2*self.request.retires)

