"""empty message

Revision ID: 8d59a28123fc
Revises: 6e69d8ab1ad2
Create Date: 2020-02-24 16:02:40.873212

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d59a28123fc'
down_revision = '6e69d8ab1ad2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('''
        ALTER TABLE "user"
        ALTER COLUMN gender
        TYPE VARCHAR(10)
        USING CASE
                WHEN gender = false THEN 'female'
                WHEN gender = true THEN 'male'
                WHEN gender is NULL THEN null
              END;
    ''')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###