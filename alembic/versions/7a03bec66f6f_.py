"""empty message

Revision ID: 7a03bec66f6f
Revises: 380390152fa0
Create Date: 2019-10-16 14:29:31.602388

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '7a03bec66f6f'
down_revision = '380390152fa0'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        '''
        ALTER TABLE "user"
            RENAME COLUMN password TO _password;
    '''
    )


def downgrade():
    op.execute(
        '''
        ALTER TABLE "user"
            RENAME COLUMN _password TO password;
    '''
    )
