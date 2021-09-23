"""empty message

Revision ID: c30d65cd3033
Revises: 70287c7fcbf4
Create Date: 2020-03-10 23:39:41.734769

"""
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql

from alembic import op


# revision identifiers, used by Alembic.
revision = 'c30d65cd3033'
down_revision = '70287c7fcbf4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'verification',
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('_code', sa.Unicode(length=6), nullable=False),
        sa.Column('expire_at', sa.DateTime(), nullable=False),
        sa.Column('type', sa.Unicode(length=10), nullable=False),
        sa.Column(
            'phone_number',
            sqlalchemy_utils.types.phone_number.PhoneNumberType(length=20),
            nullable=True,
        ),
        sa.Column(
            'email', sqlalchemy_utils.types.email.EmailType(length=255), nullable=True
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('verification_pkey')),
        sa.UniqueConstraint('id', name=op.f('verification_id_key')),
    )
    op.drop_table('verify')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'verify',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('code', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            'expire_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False
        ),
        sa.Column(
            'created', postgresql.TIMESTAMP(), autoincrement=False, nullable=False
        ),
        sa.Column(
            'updated', postgresql.TIMESTAMP(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='verify_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='verify_pkey'),
        sa.UniqueConstraint('id', name='verify_id_key'),
    )
    op.drop_table('verification')
    # ### end Alembic commands ###
