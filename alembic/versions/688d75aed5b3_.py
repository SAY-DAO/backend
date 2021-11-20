"""empty message

Revision ID: 688d75aed5b3
Revises: 7583d200b34a
Create Date: 2021-11-19 23:20:59.520934

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '688d75aed5b3'
down_revision = '7583d200b34a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f('user_avatarUrl_key'), 'user', ['avatarUrl'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('user_avatarUrl_key'), 'user', type_='unique')
    # ### end Alembic commands ###
