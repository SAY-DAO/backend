"""empty message

Revision ID: 04db12d9fe52
Revises: 68cdc5cf713e
Create Date: 2021-12-14 22:42:13.484684

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


# revision identifiers, used by Alembic.
revision = '04db12d9fe52'
down_revision = '68cdc5cf713e'
branch_labels = None
depends_on = None


def upgrade():
    import say

    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('social_worker', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.execute(
        '''UPDATE social_worker SET deleted_at = now() where "is_deleted" = true;'''
    )
    op.create_unique_constraint(
        op.f('social_worker_avatar_url_key'), 'social_worker', ['avatar_url']
    )
    op.create_unique_constraint(
        op.f('social_worker_email_key'), 'social_worker', ['email']
    )
    op.create_unique_constraint(
        op.f('social_worker_id_card_url_key'), 'social_worker', ['id_card_url']
    )
    op.create_index(
        op.f('social_worker_ngo_id_idx'), 'social_worker', ['ngo_id'], unique=False
    )
    op.create_unique_constraint(
        op.f('social_worker_passport_url_key'), 'social_worker', ['passport_url']
    )
    op.create_unique_constraint(
        op.f('social_worker_phone_number_key'), 'social_worker', ['phone_number']
    )
    op.create_index(
        op.f('social_worker_type_id_idx'), 'social_worker', ['type_id'], unique=False
    )
    op.create_unique_constraint(
        op.f('social_worker_username_key'), 'social_worker', ['username']
    )
    op.drop_constraint('social_worker_avatarUrl_key', 'social_worker', type_='unique')
    op.drop_constraint('social_worker_emailAddress_key', 'social_worker', type_='unique')
    op.drop_constraint('social_worker_idCardUrl_key', 'social_worker', type_='unique')
    op.drop_index('social_worker_id_ngo_idx', table_name='social_worker')
    op.drop_index('social_worker_id_type_idx', table_name='social_worker')
    op.drop_index('social_worker_isDeleted_idx', table_name='social_worker')
    op.drop_constraint('social_worker_passportUrl_key', 'social_worker', type_='unique')
    op.drop_constraint('social_worker_phoneNumber_key', 'social_worker', type_='unique')
    op.drop_constraint('social_worker_userName_key', 'social_worker', type_='unique')
    op.drop_column('social_worker', 'is_deleted')
    op.drop_column('social_worker', 'lastLogoutDate')
    op.add_column(
        'social_worker_version',
        sa.Column(
            'avatar_url', say.orm.types.LocalFile(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        'social_worker_version',
        sa.Column(
            'bank_account_card_number', sa.String(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('bank_account_number', sa.String(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column(
            'bank_account_sheba_number', sa.String(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        'social_worker_version',
        sa.Column(
            'birth_certificate_number', sa.String(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('birth_date', sa.Date(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('current_need_count', sa.Integer(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('deleted_at', sa.DateTime(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('email', sa.String(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column(
            'emergency_phone_number', sa.String(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('first_name', sa.String(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('generated_code', sa.String(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column(
            'id_card_url', say.orm.types.LocalFile(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('id_number', sa.String(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('last_login_date', sa.DateTime(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('last_name', sa.String(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('need_count', sa.Integer(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('ngo_id', sa.Integer(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('passport_number', sa.String(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column(
            'passport_url', say.orm.types.LocalFile(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('phone_number', sa.String(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('postal_address', sa.Text(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('telegram_id', sa.String(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('type_id', sa.Integer(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('username', sa.String(), autoincrement=False, nullable=True),
    )
    op.create_index(
        op.f('social_worker_version_ngo_id_idx'),
        'social_worker_version',
        ['ngo_id'],
        unique=False,
    )
    op.create_index(
        op.f('social_worker_version_type_id_idx'),
        'social_worker_version',
        ['type_id'],
        unique=False,
    )
    op.drop_index('social_worker_version_id_ngo_idx', table_name='social_worker_version')
    op.drop_index('social_worker_version_id_type_idx', table_name='social_worker_version')
    op.drop_index(
        'social_worker_version_isDeleted_idx', table_name='social_worker_version'
    )
    op.drop_column('social_worker_version', 'phoneNumber')
    op.drop_column('social_worker_version', 'userName')
    op.drop_column('social_worker_version', 'firstName')
    op.drop_column('social_worker_version', 'birthDate')
    op.drop_column('social_worker_version', 'id_type')
    op.drop_column('social_worker_version', 'birthCertificateNumber')
    op.drop_column('social_worker_version', 'generatedCode')
    op.drop_column('social_worker_version', 'idNumber')
    op.drop_column('social_worker_version', 'lastLogoutDate')
    op.drop_column('social_worker_version', 'id_ngo')
    op.drop_column('social_worker_version', 'currentNeedCount')
    op.drop_column('social_worker_version', 'passportNumber')
    op.drop_column('social_worker_version', 'lastLoginDate')
    op.drop_column('social_worker_version', 'emailAddress')
    op.drop_column('social_worker_version', 'telegramId')
    op.drop_column('social_worker_version', 'isDeleted')
    op.drop_column('social_worker_version', 'avatarUrl')
    op.drop_column('social_worker_version', 'bankAccountNumber')
    op.drop_column('social_worker_version', 'needCount')
    op.drop_column('social_worker_version', 'bankAccountShebaNumber')
    op.drop_column('social_worker_version', 'emergencyPhoneNumber')
    op.drop_column('social_worker_version', 'bankAccountCardNumber')
    op.drop_column('social_worker_version', 'postalAddress')
    op.drop_column('social_worker_version', 'passportUrl')
    op.drop_column('social_worker_version', 'idCardUrl')
    op.drop_column('social_worker_version', 'lastName')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'social_worker_version',
        sa.Column('lastName', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('idCardUrl', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('passportUrl', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('postalAddress', sa.TEXT(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column(
            'bankAccountCardNumber', sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        'social_worker_version',
        sa.Column(
            'emergencyPhoneNumber', sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        'social_worker_version',
        sa.Column(
            'bankAccountShebaNumber', sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('needCount', sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('bankAccountNumber', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('avatarUrl', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('isDeleted', sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('telegramId', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('emailAddress', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column(
            'lastLoginDate', postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('passportNumber', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('currentNeedCount', sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('id_ngo', sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column(
            'lastLogoutDate', postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('idNumber', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('generatedCode', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column(
            'birthCertificateNumber', sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('id_type', sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('birthDate', sa.DATE(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('firstName', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('userName', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'social_worker_version',
        sa.Column('phoneNumber', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.create_index(
        'social_worker_version_isDeleted_idx',
        'social_worker_version',
        ['isDeleted'],
        unique=False,
    )
    op.create_index(
        'social_worker_version_id_type_idx',
        'social_worker_version',
        ['id_type'],
        unique=False,
    )
    op.create_index(
        'social_worker_version_id_ngo_idx',
        'social_worker_version',
        ['id_ngo'],
        unique=False,
    )
    op.drop_index(
        op.f('social_worker_version_type_id_idx'), table_name='social_worker_version'
    )
    op.drop_index(
        op.f('social_worker_version_ngo_id_idx'), table_name='social_worker_version'
    )
    op.drop_column('social_worker_version', 'username')
    op.drop_column('social_worker_version', 'type_id')
    op.drop_column('social_worker_version', 'telegram_id')
    op.drop_column('social_worker_version', 'postal_address')
    op.drop_column('social_worker_version', 'phone_number')
    op.drop_column('social_worker_version', 'passport_url')
    op.drop_column('social_worker_version', 'passport_number')
    op.drop_column('social_worker_version', 'ngo_id')
    op.drop_column('social_worker_version', 'need_count')
    op.drop_column('social_worker_version', 'last_name')
    op.drop_column('social_worker_version', 'last_login_date')
    op.drop_column('social_worker_version', 'id_number')
    op.drop_column('social_worker_version', 'id_card_url')
    op.drop_column('social_worker_version', 'generated_code')
    op.drop_column('social_worker_version', 'first_name')
    op.drop_column('social_worker_version', 'emergency_phone_number')
    op.drop_column('social_worker_version', 'email')
    op.drop_column('social_worker_version', 'deleted_at')
    op.drop_column('social_worker_version', 'current_need_count')
    op.drop_column('social_worker_version', 'birth_date')
    op.drop_column('social_worker_version', 'birth_certificate_number')
    op.drop_column('social_worker_version', 'bank_account_sheba_number')
    op.drop_column('social_worker_version', 'bank_account_number')
    op.drop_column('social_worker_version', 'bank_account_card_number')
    op.drop_column('social_worker_version', 'avatar_url')
    op.add_column(
        'social_worker',
        sa.Column(
            'lastLogoutDate', postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        'social_worker',
        sa.Column(
            'is_deleted',
            sa.BOOLEAN(),
            server_default=sa.text('false'),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.create_unique_constraint(
        'social_worker_userName_key', 'social_worker', ['username']
    )
    op.create_unique_constraint(
        'social_worker_phoneNumber_key', 'social_worker', ['phone_number']
    )
    op.create_unique_constraint(
        'social_worker_passportUrl_key', 'social_worker', ['passport_url']
    )
    op.create_index(
        'social_worker_isDeleted_idx', 'social_worker', ['is_deleted'], unique=False
    )
    op.create_index(
        'social_worker_id_type_idx', 'social_worker', ['type_id'], unique=False
    )
    op.create_index('social_worker_id_ngo_idx', 'social_worker', ['ngo_id'], unique=False)
    op.create_unique_constraint(
        'social_worker_idCardUrl_key', 'social_worker', ['id_card_url']
    )
    op.create_unique_constraint(
        'social_worker_emailAddress_key', 'social_worker', ['email']
    )
    op.create_unique_constraint(
        'social_worker_avatarUrl_key', 'social_worker', ['avatar_url']
    )
    op.drop_constraint(
        op.f('social_worker_username_key'), 'social_worker', type_='unique'
    )
    op.drop_index(op.f('social_worker_type_id_idx'), table_name='social_worker')
    op.drop_constraint(
        op.f('social_worker_phone_number_key'), 'social_worker', type_='unique'
    )
    op.drop_constraint(
        op.f('social_worker_passport_url_key'), 'social_worker', type_='unique'
    )
    op.drop_index(op.f('social_worker_ngo_id_idx'), table_name='social_worker')
    op.drop_constraint(
        op.f('social_worker_id_card_url_key'), 'social_worker', type_='unique'
    )
    op.drop_constraint(op.f('social_worker_email_key'), 'social_worker', type_='unique')
    op.drop_constraint(
        op.f('social_worker_avatar_url_key'), 'social_worker', type_='unique'
    )
    op.drop_column('social_worker', 'deleted_at')
    # ### end Alembic commands ###
