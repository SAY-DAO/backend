"""empty message

Revision ID: 7583d200b34a
Revises: d798f4a05f9b
Create Date: 2021-11-16 21:00:08.185449

"""
import sqlalchemy as sa
from werkzeug.datastructures import FileStorage

from alembic import op


# revision identifiers, used by Alembic.
revision = '7583d200b34a'
down_revision = 'd798f4a05f9b'
branch_labels = None
depends_on = None


def upgrade():
    from say.models import User
    from say.orm import init_model
    from say.orm import session

    init_model(op.get_bind())

    conn = op.get_bind()
    user_avatars = conn.execute("""SELECT id, "avatarUrl" from "user";""").fetchall()

    all_users = session.query(User)
    total_count = all_users.count()
    print(f'Migration user avatars, total count: {total_count}')
    for i, user in enumerate(all_users):
        print(f'#{i}/{total_count}, user avatar #{user.id}')
        raw_user = list(filter(lambda u: u[0] == user.id, user_avatars))[0]
        avatar = raw_user[1]

        if avatar is None:
            continue

        if avatar == '' or avatar == '/public/resources/img/default-avatar.png':
            user.avatarUrl = None
            session.commit()
            continue

        avatar = avatar[1:]

        try:
            with open(avatar, 'rb') as f:
                user.avatarUrl = FileStorage(filename=avatar, stream=f)
                session.commit()
        except FileNotFoundError:
            continue


def downgrade():
    pass
