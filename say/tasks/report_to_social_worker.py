from say.api import celery
from say.models.social_worker_model import SocialWorker


@celery.task(base=celery.DBTask, bind=True, max_retries=2)
def report_to_social_workers(self):
    try:
        social_workers_id = self.session.query(SocialWorker.id)
        for social_worker_id, in social_workers_id:
            report_to_social_worker.delay(social_worker_id)
    except NameError:
        self.retry(countdown=3**self.request.retries)


@celery.task(base=celery.DBTask, bind=True)
def report_to_social_worker(self, social_worker_id):
    social_worker = self.session.query(SocialWorker).get(social_worker_id)
    return social_worker.send_report()

