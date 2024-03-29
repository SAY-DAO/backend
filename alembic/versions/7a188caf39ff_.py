"""empty message

Revision ID: 7a188caf39ff
Revises: 3b93cabb4df2
Create Date: 2022-04-05 17:33:28.944573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a188caf39ff'
down_revision = '3b93cabb4df2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('states', sa.Column('country_name', sa.Unicode(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('states', 'country_name')
    # ### end Alembic commands ###
