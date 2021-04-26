"""empty message

Revision ID: 6f94b8d9ffe6
Revises: 9ebc48eeec12
Create Date: 2019-11-10 16:55:20.622804

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '6f94b8d9ffe6'
down_revision = '9ebc48eeec12'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE need
            ADD COLUMN status INTEGER DEFAULT 0 NOT NULL;
    ''')


def downgrade():
    pass
