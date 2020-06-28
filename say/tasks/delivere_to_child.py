from datetime import datetime, timedelta
from sqlalchemy import and_, or_

from say.api import celery

# This task is a temporary social worker that deliver a product to child
@celery.task(base=celery.DBTask, bind=True, max_retries=2)
def change_need_status_to_delivered(self, need_id):
    from say.models.need_model import Need
    try:
        need = self.session.query(Need).get(need_id)
        need.status = 5
        need.child_delivery_date = need.ngo_delivery_date
        self.session.commit()
    except Exception as ex:
        print(str(ex))
        self.session.rollback()
        self.retry(countdown=3**self.request.retries)
        raise

    return need.id


@celery.task(base=celery.DBTask, bind=True)
def delivere_to_child(self):
    from say.models.need_model import Need
    needs_id = self.session.query(Need.id) \
        .filter(
            Need.type == 1,
            Need.status == 4,
            datetime.utcnow() - Need.ngo_delivery_date >= timedelta(hours=4),
        )

    t = []
    for need_id in needs_id:
        t.append(need_id)
        change_need_status_to_delivered.delay(need_id)
    return f'OMG! these needs are mysterious: {t}'
