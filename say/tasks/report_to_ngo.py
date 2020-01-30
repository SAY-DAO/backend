from say.api import celery
from say.models.ngo_model import Ngo


@celery.task(base=celery.DBTask, bind=True)
def report_to_ngos(self):
    ngos = self.session.query(Ngo)
    for ngo in ngos:
        report_to_ngo.delay(ngo.id)
    return


@celery.task(base=celery.DBTask, bind=True)
def report_to_ngo(self, ngo_id):
    ngo = self.session.query(Ngo).get(ngo_id)
    return ngo.send_report_to_ngo()

