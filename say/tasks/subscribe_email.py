from say.app import celery, app
from say.mailerlite import mailerlite


@celery.task()
def subscribe_email(group_id, data):
    with app.app_context():
        return mailerlite.groups.add_subscribers(
            group_id,
            [data],
            as_json=True,
        )
