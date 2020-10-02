from sqlalchemy import or_

from say.api import celery


@celery.task(base=celery.DBTask, bind=True, queue='slow')
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
            Need.link.isnot(None),
        )

    t = []
    for need in needs:
        t.append(need.id)
        update_need.delay(need.id)

    return t


@celery.task(
    base=celery.DBTask,
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 1},
    queue='slow',
)
def update_need(self, need_id, force=False):
    from say.models.need_model import Need
    need = self.session.query(Need) \
        .with_for_update() \
        .get(need_id)

    data = need.update()
    self.session.commit()

    return data
