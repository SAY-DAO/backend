"""empty message

Revision ID: ab5848477bc6
Revises: 51cfe2e110f3
Create Date: 2022-03-28 23:09:58.234686

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'ab5848477bc6'
down_revision = '51cfe2e110f3'
branch_labels = None
depends_on = None


def upgrade():
    from say.models import ChildMigration
    from say.orm import init_model
    from say.orm import session

    init_model(op.get_bind())

    op.execute(
        '''UPDATE need n set created_by_id = (select c.id_social_worker from child c where n.child_id = c.id);'''
    )

    for cm in session.query(ChildMigration).order_by(ChildMigration.migrated_at.desc()):
        cmd = f'''UPDATE need n set created_by_id = {cm.old_sw_id} where n.child_id = {cm.child_id} and n.created < '{cm.migrated_at}';'''
        op.execute(cmd)
        print(cmd)


def downgrade():
    pass
