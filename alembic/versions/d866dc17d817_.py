"""empty message

Revision ID: d866dc17d817
Revises: c0eb2faca9f7
Create Date: 2021-12-11 19:06:59.845321

"""
import sqlalchemy as sa
import sqlalchemy_utils

from alembic import op


# revision identifiers, used by Alembic.
revision = 'd866dc17d817'
down_revision = 'c0eb2faca9f7'
branch_labels = None
depends_on = None


def upgrade():
    import say

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'social_worker_version',
        sa.Column('created', sa.DateTime(), autoincrement=False, nullable=True),
        sa.Column('updated', sa.DateTime(), autoincrement=False, nullable=True),
        sa.Column('is_active', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
        sa.Column('generatedCode', sa.String(), autoincrement=False, nullable=True),
        sa.Column('id_ngo', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('id_type', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('country', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('city', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('firstName', sa.String(), autoincrement=False, nullable=True),
        sa.Column('lastName', sa.String(), autoincrement=False, nullable=True),
        sa.Column('userName', sa.String(), autoincrement=False, nullable=True),
        sa.Column('_password', sa.String(length=256), autoincrement=False, nullable=True),
        sa.Column(
            'birthCertificateNumber', sa.String(), autoincrement=False, nullable=True
        ),
        sa.Column('idNumber', sa.String(), autoincrement=False, nullable=True),
        sa.Column(
            'idCardUrl', say.orm.types.LocalFile(), autoincrement=False, nullable=True
        ),
        sa.Column('passportNumber', sa.String(), autoincrement=False, nullable=True),
        sa.Column(
            'passportUrl', say.orm.types.LocalFile(), autoincrement=False, nullable=True
        ),
        sa.Column('gender', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('birthDate', sa.Date(), autoincrement=False, nullable=True),
        sa.Column('phoneNumber', sa.String(), autoincrement=False, nullable=True),
        sa.Column(
            'emergencyPhoneNumber', sa.String(), autoincrement=False, nullable=True
        ),
        sa.Column('emailAddress', sa.String(), autoincrement=False, nullable=True),
        sa.Column('telegramId', sa.String(), autoincrement=False, nullable=True),
        sa.Column('postalAddress', sa.Text(), autoincrement=False, nullable=True),
        sa.Column(
            'avatarUrl', say.orm.types.LocalFile(), autoincrement=False, nullable=True
        ),
        sa.Column('needCount', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('currentNeedCount', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('bankAccountNumber', sa.String(), autoincrement=False, nullable=True),
        sa.Column(
            'bankAccountShebaNumber', sa.String(), autoincrement=False, nullable=True
        ),
        sa.Column(
            'bankAccountCardNumber', sa.String(), autoincrement=False, nullable=True
        ),
        sa.Column('lastLoginDate', sa.DateTime(), autoincrement=False, nullable=True),
        sa.Column('lastLogoutDate', sa.DateTime(), autoincrement=False, nullable=True),
        sa.Column('isDeleted', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column(
            'locale',
            sqlalchemy_utils.types.locale.LocaleType(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            'id', 'transaction_id', name=op.f('social_worker_version_pkey')
        ),
    )
    op.create_index(
        op.f('social_worker_version_end_transaction_id_idx'),
        'social_worker_version',
        ['end_transaction_id'],
        unique=False,
    )
    op.create_index(
        op.f('social_worker_version_id_ngo_idx'),
        'social_worker_version',
        ['id_ngo'],
        unique=False,
    )
    op.create_index(
        op.f('social_worker_version_id_type_idx'),
        'social_worker_version',
        ['id_type'],
        unique=False,
    )
    op.create_index(
        op.f('social_worker_version_isDeleted_idx'),
        'social_worker_version',
        ['isDeleted'],
        unique=False,
    )
    op.create_index(
        op.f('social_worker_version_operation_type_idx'),
        'social_worker_version',
        ['operation_type'],
        unique=False,
    )
    op.create_index(
        op.f('social_worker_version_transaction_id_idx'),
        'social_worker_version',
        ['transaction_id'],
        unique=False,
    )
    op.create_table(
        'transaction_changes',
        sa.Column('transaction_id', sa.BigInteger(), nullable=False),
        sa.Column('entity_name', sa.Unicode(length=255), nullable=False),
        sa.PrimaryKeyConstraint(
            'transaction_id', 'entity_name', name=op.f('transaction_changes_pkey')
        ),
    )
    op.create_table(
        'transaction',
        sa.Column('issued_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('remote_addr', sa.String(length=50), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['social_worker.id'],
            name=op.f('transaction_user_id_social_worker_fkey'),
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('transaction_pkey')),
    )
    op.create_index(
        op.f('transaction_user_id_idx'), 'transaction', ['user_id'], unique=False
    )
    op.drop_column('social_worker', 'childCount')
    op.drop_column('social_worker', 'currentChildCount')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'social_worker',
        sa.Column(
            'currentChildCount',
            sa.INTEGER(),
            server_default=sa.text('0'),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        'social_worker',
        sa.Column(
            'childCount',
            sa.INTEGER(),
            server_default=sa.text('0'),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_index(op.f('transaction_user_id_idx'), table_name='transaction')
    op.drop_table('transaction')
    op.drop_table('transaction_changes')
    op.drop_index(
        op.f('social_worker_version_transaction_id_idx'),
        table_name='social_worker_version',
    )
    op.drop_index(
        op.f('social_worker_version_operation_type_idx'),
        table_name='social_worker_version',
    )
    op.drop_index(
        op.f('social_worker_version_isDeleted_idx'), table_name='social_worker_version'
    )
    op.drop_index(
        op.f('social_worker_version_id_type_idx'), table_name='social_worker_version'
    )
    op.drop_index(
        op.f('social_worker_version_id_ngo_idx'), table_name='social_worker_version'
    )
    op.drop_index(
        op.f('social_worker_version_end_transaction_id_idx'),
        table_name='social_worker_version',
    )
    op.drop_table('social_worker_version')
    # ### end Alembic commands ###
