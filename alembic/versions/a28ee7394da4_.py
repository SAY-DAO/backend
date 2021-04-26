"""empty message

Revision ID: a28ee7394da4
Revises: 055a45bebde1
Create Date: 2020-02-01 22:56:34.892730

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'a28ee7394da4'
down_revision = '055a45bebde1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('need_family', 'id_family',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('nextval(\'"need_family_Id_family_seq"\'::regclass)'))
    op.alter_column('need_family', 'paid',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('0'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('need_family', 'paid',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_server_default=sa.text('0'))
    op.alter_column('need_family', 'id_family',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_server_default=sa.text('nextval(\'"need_family_Id_family_seq"\'::regclass)'))
    # ### end Alembic commands ###
