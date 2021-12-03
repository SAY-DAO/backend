"""Reset socail workers password

Revision ID: 63d467d5fdfd
Revises: adbc4f3af072
Create Date: 2021-11-28 22:12:08.657961

"""
import smtplib
from typing import DefaultDict

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '63d467d5fdfd'
down_revision = 'adbc4f3af072'
branch_labels = None
depends_on = None


def upgrade():
    from say.app import app
    from say.models import SocialWorker
    from say.orm import init_model
    from say.orm import session

    init_model(op.get_bind())
    sw_counts = DefaultDict(int)

    for sw in session.query(SocialWorker):
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
        session.commit()

        with app.app_context():
            try:
                sw.send_password(raw_password, delay=False)
                print('Username and password sent!\n')

            except smtplib.SMTPRecipientsRefused:
                print(f'Can not send password: ' f'{sw.id}\n')


def downgrade():
    pass
