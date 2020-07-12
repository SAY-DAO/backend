from say.app import celery
from say.sms import sms_provider


@celery.task(bind=True, max_retries=2)
def send_sms(self, to, text):
    try:
        return sms_provider.send(to, text)
    except:
        self.retry(countdown=2*self.request.retires)
