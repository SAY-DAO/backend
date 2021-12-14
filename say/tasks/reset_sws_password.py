import smtplib
from typing import DefaultDict

from say.celery import celery


@celery.task(base=celery.DBTask, bind=True)
def reset_sws_password(self):
    from say.app import app
    from say.models import SocialWorker

    sw_counts = DefaultDict(int)

    with app.app_context():
        for sw in self.session.query(SocialWorker):
            raw_password = SocialWorker.generate_password()
            sw.password = raw_password
            print(f'Reseting username and passowrd of {sw.id}...')

            if sw.ngo_id != 3:
                sw_counts[sw.ngo_id] += 1
                sw.username = (
                    'sw'
                    + format(sw.ngo_id, '03d')
                    + format(
                        sw_counts[sw.ngo_id],
                        '03d',
                    )
                )

            print('Username and password changed!\n')
            self.session.commit()

            try:
                sw.send_password(raw_password)
                print('Username and password sent!\n')

            except smtplib.SMTPRecipientsRefused:
                print(f'Can not send password: {sw.id}\n')
