"""empty message

Revision ID: 48b6f37c9fcd
Revises: 9f7fa375c9cb
Create Date: 2019-10-30 19:47:02.996372

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '48b6f37c9fcd'
down_revision = '9f7fa375c9cb'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE payment
            ALTER COLUMN donate TYPE INTEGER;
    ''')


def downgrade():
    op.execute('''
        ALTER TABLE payment
            ALTER COLUMN donate TYPE FLOAT;
    ''')
