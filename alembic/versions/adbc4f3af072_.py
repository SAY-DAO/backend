"""empty message

Revision ID: adbc4f3af072
Revises: 688d75aed5b3
Create Date: 2021-11-23 13:21:50.192526

"""
import sqlalchemy as sa
from werkzeug.datastructures import FileStorage

from alembic import op


# revision identifiers, used by Alembic.
revision = 'adbc4f3af072'
down_revision = '688d75aed5b3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    from say.models import SocialWorker
    from say.orm import init_model
    from say.orm import session

    init_model(op.get_bind())

    conn = op.get_bind()
    user_avatars = conn.execute(
        """SELECT id, "avatarUrl", "idCardUrl", "passportUrl" from "social_worker";"""
    ).fetchall()

    all_users = session.query(SocialWorker)
    total_count = all_users.count()
    print(f'Migration sw files, total count: {total_count}')
    for i, user in enumerate(all_users):
        print(f'#{i}/{total_count}, user avatar #{user.id}')
        raw_user = list(filter(lambda u: u[0] == user.id, user_avatars))[0]

        if not raw_user[1]:
            user.avatar = None
            session.commit()
        else:
            avatar = raw_user[1][1:]
            try:
                with open(avatar, 'rb') as f:
                    user.avatarUrl = FileStorage(f, filename=avatar)
                    session.commit()
            except FileNotFoundError:
                pass

        if not raw_user[2]:
            user.idCardUrl = None
            session.commit()
        else:
            idCardUrl = raw_user[2][1:]
            try:
                with open(idCardUrl, 'rb') as f:
                    user.idCardUrl = FileStorage(f, filename=idCardUrl)
                    session.commit()
            except FileNotFoundError:
                pass

        if not raw_user[3] or raw_user[3] == '/':
            user.passportUrl = None
            session.commit()
        else:
            passportUrl = raw_user[3][1:]
            try:
                with open(passportUrl, 'rb') as f:
                    user.passportUrl = FileStorage(f, filename=passportUrl)
                    session.commit()
            except FileNotFoundError:
                pass

    op.create_unique_constraint(
        op.f('social_worker_avatarUrl_key'), 'social_worker', ['avatarUrl']
    )
    op.create_unique_constraint(
        op.f('social_worker_idCardUrl_key'), 'social_worker', ['idCardUrl']
    )
    op.create_unique_constraint(
        op.f('social_worker_passportUrl_key'), 'social_worker', ['passportUrl']
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        op.f('social_worker_passportUrl_key'), 'social_worker', type_='unique'
    )
    op.drop_constraint(
        op.f('social_worker_idCardUrl_key'), 'social_worker', type_='unique'
    )
    op.drop_constraint(
        op.f('social_worker_avatarUrl_key'), 'social_worker', type_='unique'
    )
    # ### end Alembic commands ###
