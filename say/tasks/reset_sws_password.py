import smtplib
from typing import DefaultDict

import celery


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

            if sw.id_ngo != 3:
                sw_counts[sw.id_ngo] += 1
                sw.userName = (
                    'sw'
                    + format(sw.id_ngo, '03d')
                    + format(
                        sw_counts[sw.id_ngo],
                        '03d',
                    )
                )

            print('Username and password changed!\n')
            self.session.commit()

            try:
                sw.send_password(raw_password, delay=False)
                print('Username and password sent!\n')

            except smtplib.SMTPRecipientsRefused:
                print(f'Can not send password: {sw.id}\n')
