import os
from datetime import datetime
from datetime import timedelta
from functools import partial

from sqlalchemy import or_

from say.celery import celery
from say.config import configs
from say.langs import LANGS
from say.locale import ChangeLocaleTo
from say.render_template_i18n import render_template_i18n

from .send_email import send_embeded_subject_email


@celery.task(base=celery.DBTask, bind=True)
def report_to_families(self):
    from say.models.family_model import Family

    families_id = self.session.query(Family.id)
    # for family_id in families_id:
        # report_to_family.delay(family_id[0]) // Deprecated in favor of Nest js scheduler


@celery.task(base=celery.DBTask, bind=True)
def report_to_family(self, family_id):
    from say.app import app
    from say.models.child_model import Child
    from say.models.family_model import Family
    from say.models.need_family_model import NeedFamily
    from say.models.need_model import Need
    from say.models.user_family_model import UserFamily
    from say.models.user_model import User

    session = self.session
    yesterday = datetime.utcnow() - timedelta(days=1)

    with app.app_context(), ChangeLocaleTo(LANGS.fa):
        family = session.query(Family).get(family_id)

        child_id, child_sayName = (
            session.query(Child.id, Child.sayName).filter_by(id=family.id_child).one()
        )

        # TODO: Getting whole need object beacuse of hybrid status_descrption
        # Getting needs that status of them updated in from yesterday
        needs = (
            session.query(Need)
            .filter_by(child_id=child_id)
            .filter(Need.status_updated_at > yesterday)
            .filter(Need.status >= 2)
            .filter(or_(Need.type == 0, Need.status != 4))
            .order_by(Need.status)
            .all()
        )

        if len(needs) == 0:
            return

        # Joining by NeedFamily and geting distinct emails
        to_members_email = [
            u.emailAddress
            for u in session.query(User.emailAddress)
            .filter(User.id == NeedFamily.id_user)
            .filter(User.emailAddress.isnot(None))
            .filter(User.receive_email.is_(True))
            .filter(NeedFamily.id_family == family_id)
            .filter(NeedFamily.id_need.in_([need.id for need in needs]))
            .distinct()
        ]

        # Joining by UserFamily and geting distinct emails
        all_members_email = [
            u.emailAddress
            for u in session.query(User.emailAddress)
            .filter(User.id == UserFamily.id_user)
            .filter(User.emailAddress.isnot(None))
            .filter(User.receive_email.is_(True))
            .filter(UserFamily.id_family == family_id)
            .filter(UserFamily.isDeleted.is_(False))
            .distinct()
        ]

        cc_members_email = list(set(all_members_email) - set(to_members_email))
        to_members_email = list(
            set(to_members_email).intersection(set(all_members_email))
        )
        base_url = configs.BASE_URL
        child_page = os.path.join(base_url, 'childPage', str(child_id), '0')

        report_email = partial(
            send_embeded_subject_email.delay,
            html=render_template_i18n(
                'status_update_to_family.html',
                child_sayName=child_sayName,
                needs=needs,
                yesterday_date=yesterday,
                child_page=child_page,
                locale=LANGS.fa,
                date_with_year=False,
            ),
        )

        for email in to_members_email:
            report_email(to=email)

        for email in cc_members_email:
            report_email(
                to=configs.FAMILY_REPORT_EMAIL,
                cc=email,
            )

    return [to_members_email, cc_members_email]
