"""empty message

Revision ID: 55e18f69e99e
Revises: 76731d966b0e
Create Date: 2019-10-20 17:08:32.732613

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55e18f69e99e'
down_revision = '76731d966b0e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE need
            ADD COLUMN doing_duration INTEGER DEFAULT 5 NOT NULL;
    ''')

def downgrade():
    op.execute('''
        ALTER TABLE need
            DROP COLUMN doing_duration;
    ''')
