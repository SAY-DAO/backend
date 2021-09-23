"""empty message

Revision ID: 656b67f31482
Revises: 3bc6777703aa
Create Date: 2019-11-11 16:11:21.741930

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '656b67f31482'
down_revision = '3bc6777703aa'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        '''
        ALTER TABLE need
            ADD COLUMN link TEXT;
    '''
    )


def downgrade():
    pass
