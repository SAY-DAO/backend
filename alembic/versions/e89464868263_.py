"""empty message

Revision ID: e89464868263
Revises: c30d65cd3033
Create Date: 2020-03-11 18:25:13.392787

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'e89464868263'
down_revision = 'c30d65cd3033'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f('verification_id_key'), 'verification', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('verification_id_key'), 'verification', type_='unique')
    # ### end Alembic commands ###
