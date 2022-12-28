from time import sleep

from sqlalchemy import or_

from say.celery import celery
from say.orm import safe_commit


@celery.task(base=celery.DBTask, bind=True, queue='slow')
def update_needs(self):
    from say.models.need_model import Need

    needs = self.session.query(Need).filter(
        Need.type == 1,
        or_(
            Need.status < 4,
            Need.title.is_(None),
        ),
        Need.isDeleted.is_(False),
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

    sleep(5)
    need = self.session.query(Need).get(need_id)
    data = need.update(force=force)
    safe_commit(self.session)

    return data
