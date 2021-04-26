"""empty message

Revision ID: 37b19dbb4242
Revises: c242455d454b
Create Date: 2020-11-13 03:20:36.129042

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


# revision identifiers, used by Alembic.
revision = '37b19dbb4242'
down_revision = 'c242455d454b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('need_family', sa.Column('type', sa.Text(), nullable=True))
    op.execute('''UPDATE need_family set type = 'app';''')
    op.execute('ALTER TABLE need_family ALTER COLUMN type SET NOT NULL;')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('need_family', 'type')
    # ### end Alembic commands ###
