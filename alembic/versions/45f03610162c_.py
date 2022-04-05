"""empty message

Revision ID: 45f03610162c
Revises: 13273160e75b
Create Date: 2022-04-05 17:39:46.837984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45f03610162c'
down_revision = '13273160e75b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cities', sa.Column('country_name', sa.Unicode(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cities', 'country_name')
    # ### end Alembic commands ###
