"""empty message

Revision ID: 884c1cd36094
Revises: 9be872f9b2ca
Create Date: 2020-02-19 18:14:14.836839

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '884c1cd36094'
down_revision = '9be872f9b2ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'country')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('country', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
