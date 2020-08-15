"""empty message

Revision ID: eb1bff1a16e3
Revises: 04432c7759dd
Create Date: 2020-08-07 21:47:47.418397

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb1bff1a16e3'
down_revision = '04432c7759dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('invitations', sa.Column('text', sa.Unicode(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('invitations', 'text')
    # ### end Alembic commands ###