from say.api import celery
from say.models.ngo_model import Ngo


@celery.task(base=celery.DBTask, bind=True)
def report_to_ngos(self):
    ngos_id = self.session.query(Ngo.id)
    for ngo_id, in ngos_id:
        report_to_ngo.delay(ngo_id)
    return


@celery.task(base=celery.DBTask, bind=True)
def report_to_ngo(self, ngo_id):
    ngo = self.session.query(Ngo).get(ngo_id)
    return ngo.send_report_to_ngo()

