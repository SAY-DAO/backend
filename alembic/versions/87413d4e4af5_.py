"""empty message

Revision ID: 87413d4e4af5
Revises: d880d9aeb59b
Create Date: 2020-04-25 17:53:00.333358

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '87413d4e4af5'
down_revision = 'd880d9aeb59b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('invitations', 'role', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column(
        'user', 'country', existing_type=sa.VARCHAR(length=8), nullable=True
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'user', 'country', existing_type=sa.VARCHAR(length=8), nullable=False
    )
    op.alter_column('invitations', 'role', existing_type=sa.INTEGER(), nullable=False)
    # ### end Alembic commands ###
