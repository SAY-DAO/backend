from datetime import datetime
from datetime import timedelta

from say.celery import celery
from say.langs import LANGS
from say.render_template_i18n import render_template_i18n

from .send_email import send_embeded_subject_email


@celery.task(base=celery.DBTask, bind=True)
def report_unpayables(self):
    from say.models import Need
    from say.models import Ngo

    unpayables = (
        self.session.query(Need)
        .filter(
            Need.unavailable_from.isnot(None),  # < datetime.utcnow(),
            Need.unpayable_from < datetime.utcnow(),
            Need.unpayable_from > datetime.utcnow() - timedelta(days=1),
            Need.isDeleted.is_(False),
            Need.isConfirmed == True,
            Need.isDone != True,
        )
        .all()
    )

    if len(unpayables) == 0:
        return

    say = (
        self.session.query(Ngo)
        .filter(
            Ngo.name == 'SAY',
        )
        .one()
    )

    say_coordinator = say.coordinator.emailAddress

    from say.app import app

    with app.app_context():
        send_embeded_subject_email.delay(
            to=say_coordinator,
            html=render_template_i18n(
                'report_unpayables.html',
                needs=unpayables,
                locale=LANGS.fa,
            ),
        )

    return [u.id for u in unpayables]
