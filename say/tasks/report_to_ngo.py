from say.api import celery
from say.models.ngo_model import NgoModel


@celery.task(base=celery.DBTask, bind=True)
def report_to_ngos(self):
    ngos = self.session.query(NgoModel)
    res = []
    for ngo in ngos:
        res.append(report_to_ngo.delay(ngo.id))
    return res

@celery.task(base=celery.DBTask, bind=True)
def report_to_ngo(self, ngo_id):
    ngo = self.session.query(NgoModel).get(ngo_id)
    return ngo.send_report_to_ngo()

