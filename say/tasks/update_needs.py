from datetime import datetime, timedelta
from sqlalchemy import and_, or_

from say.api import celery


@celery.task(base=celery.DBTask, bind=True)
def update_needs(self):
    from say.models.need_model import Need
    needs = self.session.query(Need) \
        .filter(
            Need.type == 1,
            or_(
                Need.status < 4,
                Need.title.is_(None),
            ),
            Need.isDeleted==False,
            Need.isConfirmed==True,
            Need.link.isnot(None),
        )

    t = []
    for need in needs:
        t.append(need.id)
        update_need.delay(need.id)

    return t


@celery.task(base=celery.DBTask, bind=True, max_retires=3)
def update_need(self, need_id, force=False):
    from say.models.need_model import Need
    try:
        need = self.session.query(Need) \
            .with_for_update() \
            .get(need_id)

        data = need.update()
        self.session.commit()
    except:
        self.session.rollback()
        self.retry(countdown=3**self.request.retries)

    return data


# This task is a temporary social worker that deliver a product to child
@celery.task(base=celery.DBTask, bind=True)
def change_need_status_to_delivered(self, need_id):
    from say.models.need_model import Need
    need = self.session.query(Need).get(need_id)
    need.status = 5
    need.child_delivery_date = need.ngo_delivery_date
    self.session.commit()

