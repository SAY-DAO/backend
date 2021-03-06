"""empty message

Revision ID: 253d7eaf7817
Revises: 8a0bca2890cc
Create Date: 2020-10-21 21:48:46.336643

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '253d7eaf7817'
down_revision = '8a0bca2890cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('verification', sa.Column('verified', sa.Boolean()))
    op.execute('UPDATE verification set verified = false;')
    op.execute('ALTER TABLE verification ALTER COLUMN verified SET NOT NULL;')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('verification', 'verified')
    # ### end Alembic commands ###
