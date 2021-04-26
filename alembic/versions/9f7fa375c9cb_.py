"""empty message

Revision ID: 9f7fa375c9cb
Revises: 55e18f69e99e
Create Date: 2019-10-20 18:47:42.211561

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '9f7fa375c9cb'
down_revision = '55e18f69e99e'
branch_labels = None
depends_on = None


def upgrade():
     op.execute('''
        ALTER TABLE payment
            ADD COLUMN donate INTEGER DEFAULT 0 NOT NULL;
    ''')


def downgrade():
     op.execute('''
        ALTER TABLE payment
            DROP COLUMN donate;
    ''')
