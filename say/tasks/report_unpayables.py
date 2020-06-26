from datetime import datetime, timedelta

from .send_email import send_embeded_subject_email
from say.api import celery, app
from say.langs import LANGS
from say.render_template_i18n import render_template_i18n


@celery.task(base=celery.DBTask, bind=True)
def report_unpayables(self):
    from say.models import Need, Ngo

    unpayables = self.session.query(Need).filter(
        Need.unavailable_from.isnot(None), # < datetime.utcnow(),
        Need.unpayable_from < datetime.utcnow(),
        Need.unpayable_from > datetime.utcnow() - timedelta(days=1),
        Need.isDeleted.is_(False),
        Need.isConfirmed == True,
        Need.isDone != True,
    ).all()

    if len(unpayables) == 0:
        return

    say = self.session.query(Ngo).filter(
        Ngo.name == 'SAY',
    ).one()

    say_coordinator = say.coordinator.emailAddress

    with app.app_context():
        send_embeded_subject_email(
            to=say_coordinator,
            html=render_template_i18n(
                'report_unpayables.html',
                needs=unpayables,
                locale=LANGS.fa,
            ),
        )

    return [u.id for u in unpayables]

