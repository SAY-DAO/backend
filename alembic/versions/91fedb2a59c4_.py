"""empty message

Revision ID: 91fedb2a59c4
Revises: aa02ecb3b4c8
Create Date: 2019-10-12 21:27:25.307454

"""
import sqlalchemy as sa
from sqlalchemy import Boolean
from sqlalchemy import Date
from sqlalchemy import Integer
from sqlalchemy import String

from alembic import op


# revision identifiers, used by Alembic.
revision = '91fedb2a59c4'
down_revision = 'aa02ecb3b4c8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'payment',
        sa.Column('id', Integer, nullable=False, primary_key=True),
        sa.Column('id_need', Integer, sa.ForeignKey('need.id'), nullable=False),
        sa.Column('id_user', Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('paymentId', String),
        sa.Column('orderId', String),
        sa.Column('createdAt', Date, nullable=False),
        sa.Column('link', String, nullable=True),
        sa.Column('amount', Integer, nullable=True),
        sa.Column('desc', String, nullable=True),
        sa.Column('is_verified', Boolean, nullable=True),
        sa.Column('date', Date, nullable=True),
        sa.Column('card_no', String, nullable=True),
        sa.Column('hashed_card_no', String, nullable=True),
        sa.Column('track_id', String, nullable=True),
        sa.Column('verfied_date', Date, nullable=True),
    )


def downgrade():
    op.drop_table('payment')
