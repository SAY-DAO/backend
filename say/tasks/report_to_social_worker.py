from say.api import celery
from say.models.social_worker_model import SocialWorkerModel


@celery.task(base=celery.DBTask, bind=True)
def report_to_social_workers(self):
    social_workers_id = self.session.query(SocialWorkerModel.id)
    for social_worker_id, in social_workers_id:
        report_to_social_worker.delay(social_worker_id)
    return


@celery.task(base=celery.DBTask, bind=True)
def report_to_social_worker(self, social_worker_id):
    social_worker = self.session.query(SocialWorkerModel).get(social_worker_id)
    return social_worker.send_report()

