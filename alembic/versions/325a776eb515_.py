"""empty message

Revision ID: 325a776eb515
Revises: 7edc4b2ac178
Create Date: 2020-01-31 19:53:27.378031

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '325a776eb515'
down_revision = '7edc4b2ac178'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE activity RENAME TO sw_activity')


def downgrade():
    op.execute('ALTER TABLE sw_activity RENAME TO activity')
