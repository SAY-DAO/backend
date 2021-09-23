"""Case-insetive unique constraint for userName

Revision ID: 2774278e1b7d
Revises: 8d59a28123fc
Create Date: 2020-02-25 15:41:14.681363

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '2774278e1b7d'
down_revision = '8d59a28123fc'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        '''
        CREATE UNIQUE INDEX user_username_key
        ON "user" (lower("userName"));
    '''
    )


def downgrade():
    pass
