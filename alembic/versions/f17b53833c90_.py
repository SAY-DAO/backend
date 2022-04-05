"""empty message

Revision ID: f17b53833c90
Revises: 4bddeb43ad25
Create Date: 2022-04-05 17:35:01.919110

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f17b53833c90'
down_revision = '4bddeb43ad25'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('states', 'flag',
               existing_type=sa.SMALLINT(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('states', 'flag',
               existing_type=sa.SMALLINT(),
               nullable=False)
    # ### end Alembic commands ###
