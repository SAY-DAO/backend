"""empty message

Revision ID: 76731d966b0e
Revises: 230906bf8396
Create Date: 2019-10-20 13:54:24.181421

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '76731d966b0e'
down_revision = '230906bf8396'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        '''
        ALTER TABLE child
            ADD COLUMN "sleptAvatarUrl" TEXT;
    '''
    )
    op.execute(
        '''
        UPDATE child
            SET "sleptAvatarUrl" = "avatarUrl";
    '''
    )
    op.execute(
        '''
        ALTER TABLE child
            ALTER COLUMN "sleptAvatarUrl" SET NOT NULL;
    '''
    )
    op.execute(
        '''
        ALTER TABLE child
            ALTER COLUMN "lastUpdate" TYPE TIMESTAMP WITH TIME ZONE;
    '''
    )
    op.execute(
        '''
        ALTER TABLE child
            ALTER COLUMN "createdAt" TYPE TIMESTAMP WITH TIME ZONE;
    '''
    )


def downgrade():
    op.execute(
        '''
        ALTER TABLE child
            DROP COLUMN "sleptAvatarUrl";
    '''
    )
