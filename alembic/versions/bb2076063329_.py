"""empty message

Revision ID: bb2076063329
Revises: 792e0cebae00
Create Date: 2020-01-27 16:54:14.964399

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'bb2076063329'
down_revision = '792e0cebae00'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(
        '''
        ALTER TABLE reset_password
        ADD COLUMN is_used BOOLEAN NOT NULL DEFAULT FALSE;
    '''
    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('reset_password', 'is_used')
    # ### end Alembic commands ###
