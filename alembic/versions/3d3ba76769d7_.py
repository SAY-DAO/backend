"""empty message

Revision ID: 3d3ba76769d7
Revises: 6d4d1b58534f
Create Date: 2020-01-13 21:05:42.529674

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d3ba76769d7'
down_revision = '6d4d1b58534f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('ALTER TABLE child RENAME COLUMN "doneNeedCount" TO done_needs_count')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('ALTER TABLE child RENAME COLUMN done_needs_count TO "doneNeedCount"')
    # ### end Alembic commands ###