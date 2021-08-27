"""Remove whitespace from email

Revision ID: d2111ab4a366
Revises: 581a6749804a
Create Date: 2021-08-27 09:12:10.459765

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'd2111ab4a366'
down_revision = '581a6749804a'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''UPDATE "user" set "emailAddress" = regexp_replace("emailAddress", '\s', '', 'g');''')


def downgrade():
    pass
