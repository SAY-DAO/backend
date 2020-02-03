from datetime import datetime, timedelta

from sqlalchemy import or_

from say.langs import LANGS
from say.locale import ChangeLocaleTo
from say.api import celery, app
from .send_email import send_embeded_subject_email
from say.render_template_i18n import render_template_i18n


@celery.task(base=celery.DBTask, bind=True)
def report_to_families(self):
    from say.models.family_model import Family

    families_id = self.session.query(Family.id).all()
    for family_id in families_id:
        report_to_family.delay(family_id[0])


@celery.task(base=celery.DBTask, bind=True)
def report_to_family(self, family_id):
    from say.models.user_model import User
    from say.models.need_model import Need
    from say.models.child_model import Child
    from say.models.family_model import Family
    from say.models.user_family_model import UserFamily
    from say.models.need_family_model import NeedFamily

    session = self.session
    yesterday = datetime.utcnow() - timedelta(days=1)

    with app.app_context(), ChangeLocaleTo(LANGS.fa):
        family = session.query(Family).get(family_id)

        child_id, child_sayName = session.query(Child.id, Child.sayName) \
            .filter_by(id=family.id_child) \
            .one()

        # TODO: Getting whole need object beacuse of hybrid status_descrption
        # Getting needs that status of them updated in from yesterday
        needs = session.query(Need) \
            .filter_by(child_id=child_id) \
            .filter(Need.status_updated_at > yesterday) \
            .filter(Need.status >= 2) \
            .filter(or_(Need.type == 0, Need.status != 4)) \
            .order_by(Need.status) \
            .all()

        if len(needs) == 0:
            return

        # Joining by NeedFamily and geting distinct emails
        to_members_email = [
            u.emailAddress for u in session
            .query(User.emailAddress) \
            .filter(User.id==NeedFamily.id_user) \
            .filter(NeedFamily.id_family==family_id) \
            .distinct()
        ]

        # Joining by UserFamily and geting distinct emails
        all_members_email = [
            u.emailAddress for u in session
            .query(User.emailAddress) \
            .filter(User.id==UserFamily.id_user) \
            .filter(UserFamily.id_family==family_id) \
            .distinct() \
        ]

        cc_members_email = list(set(all_members_email) - set(to_members_email))

        send_embeded_subject_email(
            to=to_members_email,
            html=render_template_i18n(
                'status_update_to_family.html',
                child_sayName=child_sayName,
                needs=needs,
                yesterday_date=yesterday,
                locale=LANGS.fa,
                date_with_year=False,
            ),
            cc=cc_members_email,
        )

    return [to_members_email, cc_members_email]
