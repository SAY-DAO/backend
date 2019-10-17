"""empty message

Revision ID: 230906bf8396
Revises: 7a03bec66f6f
Create Date: 2019-10-17 23:45:50.862379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '230906bf8396'
down_revision = '7a03bec66f6f'
branch_labels = None
depends_on = None


def upgrade():

    op.execute('''
        ALTER TABLE need
            ADD COLUMN child_id INTEGER REFERENCES child(id) ON DELETE CASCADE;
    ''')

    op.execute('''
        UPDATE need n SET  child_id = cn.id_child
            FROM child_need cn where n.id = cn.id_need;
    ''')


def downgrade():
    op.execute('''
        ALTER TABLE need
            DROP COLUMN child_id;
    ''')

