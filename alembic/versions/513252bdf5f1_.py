"""empty message

Revision ID: 513252bdf5f1
Revises: f3a2db4c91f1
Create Date: 2022-06-06 12:42:41.727070

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '513252bdf5f1'
down_revision = 'f3a2db4c91f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('receipt_version_code_idx', table_name='receipt_version')
    op.drop_index('receipt_version_end_transaction_id_idx', table_name='receipt_version')
    op.drop_index('receipt_version_operation_type_idx', table_name='receipt_version')
    op.drop_index('receipt_version_owner_id_idx', table_name='receipt_version')
    op.drop_index('receipt_version_transaction_id_idx', table_name='receipt_version')
    op.drop_table('receipt_version')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('receipt_version',
    sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('attachment', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('code', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('deleted', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('description', sa.VARCHAR(length=1024), autoincrement=False, nullable=True),
    sa.Column('title', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('is_public', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('need_status', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
    sa.Column('attachment_mod', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('code_mod', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('created_mod', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('deleted_mod', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('description_mod', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('is_public_mod', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('need_status_mod', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('owner_id_mod', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('title_mod', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('updated_mod', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id', name='receipt_version_pkey')
    )
    op.create_index('receipt_version_transaction_id_idx', 'receipt_version', ['transaction_id'], unique=False)
    op.create_index('receipt_version_owner_id_idx', 'receipt_version', ['owner_id'], unique=False)
    op.create_index('receipt_version_operation_type_idx', 'receipt_version', ['operation_type'], unique=False)
    op.create_index('receipt_version_end_transaction_id_idx', 'receipt_version', ['end_transaction_id'], unique=False)
    op.create_index('receipt_version_code_idx', 'receipt_version', ['code'], unique=False)
    # ### end Alembic commands ###
