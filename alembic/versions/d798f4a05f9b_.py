"""empty message

Revision ID: d798f4a05f9b
Revises: 1c89b563da22
Create Date: 2021-11-16 17:29:37.691218

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'd798f4a05f9b'
down_revision = '1c89b563da22'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('need_family', 'username')
    op.drop_column('need_family', 'user_avatar')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'need_family',
        sa.Column('user_avatar', sa.TEXT(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'need_family',
        sa.Column('username', sa.TEXT(), autoincrement=False, nullable=False),
    )
    # ### end Alembic commands ###
