"""empty message

Revision ID: a7f15f27dc62
Revises: 19a5d398fe58
Create Date: 2020-05-05 20:49:45.839124

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'a7f15f27dc62'
down_revision = '19a5d398fe58'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_installed', sa.Boolean(), nullable=True))
    op.execute('UPDATE "user" set is_installed = false;')
    op.execute('ALTER TABLE "user" ALTER COLUMN is_installed SET NOT NULL;')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_installed')
    # ### end Alembic commands ###
