"""empty message

Revision ID: 5c91461b0019
Revises: 6f94b8d9ffe6
Create Date: 2019-11-10 20:58:07.844019

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '5c91461b0019'
down_revision = '6f94b8d9ffe6'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE need
            ADD COLUMN donated INTEGER DEFAULT 0 NOT NULL;
    ''')


def downgrade():
    pass
