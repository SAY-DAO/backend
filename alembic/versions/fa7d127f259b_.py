"""empty message

Revision ID: fa7d127f259b
Revises: 513252bdf5f1
Create Date: 2022-09-29 19:28:49.104876

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'fa7d127f259b'
down_revision = '513252bdf5f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('need', 'category', existing_type=sa.INTEGER(), nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('need', 'category', existing_type=sa.INTEGER(), nullable=False)
    # ### end Alembic commands ###
