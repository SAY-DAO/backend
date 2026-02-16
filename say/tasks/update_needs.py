import random
from time import sleep
from datetime import datetime
# from sqlalchemy import or_, and_

from say.celery import celery
from say.orm import safe_commit


@celery.task(base=celery.DBTask, bind=True, queue='slow')
def update_needs(self):
    from say.models.need_model import Need

    # Check if today is the "right" day (every other day)
    today = datetime.now().day
    if today % 2 == 0:  # Random logic for every other day 
        # Task logic goes here (e.g., update needs)
        print("Running task on every other day!")
        needs = self.session.query(Need).filter(
            Need.type == 1,
            Need.status < 3,
            Need.isDeleted.is_(False),
            Need.link.isnot(None),
        )

        t = []
        counter = 0
        print(f"Total needs to be updated: {needs.count()}")
        for need in needs:
            counter+=1
            t.append(need.id)
            print(f"{counter}/{needs.count()}-> updating need: {need.id}")
            sleep(random.randint(30, 300)) 
            update_need.delay(need.id)

        return t
    else:
        print("Not running task today (odd day).")


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
    need = self.session.query(Need).get(need_id)    
    data = need.update(force=force)
    safe_commit(self.session)

    return data
