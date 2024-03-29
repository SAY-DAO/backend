"""empty message

Revision ID: 0297edf6ad0b
Revises: ab5848477bc6
Create Date: 2022-03-28 23:32:33.805899

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0297edf6ad0b'
down_revision = 'ab5848477bc6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('need', 'created_by_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('need', 'created_by_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
