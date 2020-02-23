"""empty message

Revision ID: 9be872f9b2ca
Revises: 1927cbecc60d
Create Date: 2020-02-19 16:53:49.635786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9be872f9b2ca'
down_revision = '1927cbecc60d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('country_code', sa.Unicode(length=8), nullable=True))
#    op.execute('''UPDATE "user" set country_code = 'IR';''')
#    op.execute('''alter table "user" alter COLUMN country_code set not null;''')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'country_code')
    # ### end Alembic commands ###
