"""empty message

Revision ID: 9b39c99f9f44
Revises: a1863d77ffa0
Create Date: 2020-04-10 18:52:21.002789

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b39c99f9f44'
down_revision = 'a1863d77ffa0'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE child
        RENAME COLUMN "avatarUrl"
           TO "awakeAvatarUrl";
    ''')


def downgrade():
    op.execute('''
        ALTER TABLE child
        RENAME COLUMN "awakeAvatarUrl"
            TO "avatarUrl";
    ''')
