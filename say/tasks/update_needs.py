from say.api import celery


@celery.task(base=celery.DBTask, bind=True)
def update_needs(self):
    from say.models.need_model import NeedModel
    needs = self.session.query(NeedModel) \
        .filter(NeedModel.type == 1) \
        .filter(NeedModel.status < 2) \
        .filter(NeedModel.isDeleted==False) \
        .filter(NeedModel.link.isnot(None))

    t = []
    for need in needs:
        t.append(need.id)
        update_need.delay(need.id)
    return t


@celery.task(base=celery.DBTask, bind=True)
def update_need(self, need_id):
    from say.models.need_model import NeedModel
    need = self.session.query(NeedModel).get(need_id)
    if need.status >= 2:
        return

    data = need.update()
    self.session.commit()
    return data


# This task is a temporary social worker that deliver a product to child
@celery.task(base=celery.DBTask, bind=True)
def change_need_status_to_delivered(self, need_id):
    from say.models.need_model import NeedModel
    need = self.session.query(NeedModel).get(need_id)
    need.status = 5
    need.child_delivery_date = need.ngo_delivery_date
    self.session.commit()

