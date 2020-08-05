"""empty message

Revision ID: d162c5703e01
Revises: 656b67f31482
Create Date: 2019-11-11 17:42:02.101896

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd162c5703e01'
down_revision = '656b67f31482'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE need
            RENAME COLUMN cost TO _cost;
    ''')


def downgrade():
    op.execute('''
        ALTER TABLE need
            RENAME COLUMN _cost TO cost;
    ''')


