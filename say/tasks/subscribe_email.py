from say.api import mailerlite, app
from say.celery import celery


@celery.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_kwargs={'max_retries': 20}
)
def subscribe_email(group_id, data):
    with app.app_context():
        return mailerlite.groups.add_subscribers(
            group_id,
            [data],
            as_json=True,
        )
