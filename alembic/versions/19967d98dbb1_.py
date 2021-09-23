"""Added phone_number index

Revision ID: 19967d98dbb1
Revises: e89464868263
Create Date: 2020-03-11 19:57:19.716206

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '19967d98dbb1'
down_revision = 'e89464868263'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('COMMIT')

    op.create_index(
        op.f('user_phone_number_idx'),
        'user',
        ['phone_number'],
        postgresql_concurrently=True,
        unique=True,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
