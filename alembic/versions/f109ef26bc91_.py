"""empty message

Revision ID: f109ef26bc91
Revises: 133ac22dd633
Create Date: 2020-01-29 20:24:57.945054

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'f109ef26bc91'
down_revision = '133ac22dd633'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'need',
        sa.Column(
            'status_updated_at',
            sa.DateTime(),
            nullable=True,
            server_default=sa.text(
                u"TIMEZONE('utc', CURRENT_TIMESTAMP) - interval '1 day'"
            ),
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('need', 'status_updated_at')
    # ### end Alembic commands ###
