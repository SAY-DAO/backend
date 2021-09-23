"""empty message

Revision ID: d594919df769
Revises: 9bcf655b54fd
Create Date: 2019-12-07 16:50:41.427234

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'd594919df769'
down_revision = '9bcf655b54fd'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        '''
        ALTER TABLE need
            ADD COLUMN "oncePurchased" BOOLEAN DEFAULT false;
    '''
    )


def downgrade():
    op.execute(
        '''
        ALTER TABLE need
            DROP COLUMN "oncePurchased";
    '''
    )
