"""empty message

Revision ID: 28d2e4c9af84
Revises: a426c0feff72
Create Date: 2020-01-15 23:27:52.297641

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '28d2e4c9af84'
down_revision = 'a426c0feff72'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('ALTER TABLE "user" RENAME COLUMN "spentCredit" TO spent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('ALTER TABLE "user" RENAME COLUMN spent TO "spentCredit"')
    # ### end Alembic commands ###
