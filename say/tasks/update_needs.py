from datetime import datetime, timedelta
from sqlalchemy import and_, or_

import say.orm
from say.api import celery


@celery.task(base=celery.DBTask, bind=True)
def update_needs(self):
    from say.models.need_model import Need
    needs = say.orm.session.query(Need) \
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


@celery.task(base=celery.DBTask, bind=True, max_retries=2)
def update_need(self, need_id, force=False):
    from say.models.need_model import Need
    try:
        need = say.orm.session.query(Need) \
            .with_for_update() \
            .get(need_id)

        data = need.update()
        say.orm.commit()
    except:
        say.orm.session.rollback()
        self.retry(countdown=3**self.request.retries)

    return data
