"""empty message

Revision ID: bb128d1d1376
Revises: 5efe79cc2116
Create Date: 2021-11-12 15:57:22.469611

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'bb128d1d1376'
down_revision = '5efe79cc2116'
branch_labels = None
depends_on = None


def fix_path(path):
    if path is None:
        return

    path = path.strip()
    if not path.startswith('/'):
        return '/' + path

    return path.replace('//', '/')


def upgrade():
    from say.models import Child
    from say.models import Need
    from say.models import Ngo
    from say.models import SocialWorker
    from say.models import User
    from say.orm import init_model
    from say.orm import session

    init_model(op.get_bind())

    needs = session.query(Need)
    for need in needs:
        need.imageUrl = fix_path(need.imageUrl)

    children = session.query(Child)
    for child in children:
        child.awakeAvatarUrl = fix_path(child.awakeAvatarUrl)
        child.sleptAvatarUrl = fix_path(child.sleptAvatarUrl)
        child.voiceUrl = fix_path(child.voiceUrl)

    users = session.query(User)
    for user in users:
        user.avatarUrl = fix_path(user.avatarUrl)

    sws = session.query(SocialWorker)
    for sw in sws:
        sw.avatarUrl = fix_path(sw.avatarUrl)
        sw.idCardUrl = fix_path(sw.idCardUrl)
        sw.passportNumber = fix_path(sw.passportNumber)

    ngos = session.query(Ngo)
    for ngo in ngos:
        ngo.logoUrl = fix_path(ngo.logoUrl)

    raise


def downgrade():
    pass
