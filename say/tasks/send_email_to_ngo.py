from . import *
from say.models.ngo_model import NgoModel


@celery.task(base=celery.DBTask, bind=True)
def send_email_to_ngo(self, ngo_id):
    ngo = self.session.query(NgoModel).get(ngo_id)
    ngo.name = ngo.name + str(1)
#    self.session.commit()
    return

