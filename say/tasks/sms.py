from say.api import sms_provider
from . import celery


@celery.task(bind=True, max_retries=2)
def send_sms(self, to, text):
    try:
        return sms_provider.send(to, text)
    except:
        self.retry(countdown=2*self.request.retires)
