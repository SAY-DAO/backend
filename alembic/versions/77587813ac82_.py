"""empty message

Revision ID: 77587813ac82
Revises: 48b6f37c9fcd
Create Date: 2019-11-06 12:59:01.985181

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '77587813ac82'
down_revision = '48b6f37c9fcd'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        '''
        ALTER TABLE need
            ADD COLUMN details TEXT;
    '''
    )


def downgrade():
    op.execute(
        '''
        ALTER TABLE need
            DROP COLUMN details;
    '''
    )
