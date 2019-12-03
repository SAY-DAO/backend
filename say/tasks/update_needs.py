from say.api import celery


@celery.task(base=celery.DBTask, bind=True)
def update_needs(self):
    from say.models.need_model import NeedModel
    needs = self.session.query(NeedModel) \
        .filter(NeedModel.link.isnot(None)) \
        .filter(NeedModel.type == 1) \
        .filter(NeedModel.status.in_([0,1]))

    for need in needs:
        update_need.delay(need.id)


@celery.task(base=celery.DBTask, bind=True)
def update_need(self, need_id):
    from say.models.need_model import NeedModel
    need = self.session.query(NeedModel).get(need_id)
    return need.update()



