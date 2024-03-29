"""empty message

Revision ID: cf604eb4dc19
Revises: d866dc17d817
Create Date: 2021-12-11 21:42:04.893937

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


# revision identifiers, used by Alembic.
revision = 'cf604eb4dc19'
down_revision = 'd866dc17d817'
branch_labels = None
depends_on = None


def upgrade():
    import say

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'child_version',
        sa.Column('created', sa.DateTime(), autoincrement=False, nullable=True),
        sa.Column('updated', sa.DateTime(), autoincrement=False, nullable=True),
        sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
        sa.Column('id_ngo', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('id_social_worker', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column(
            'firstName_translations',
            postgresql.HSTORE(text_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            'lastName_translations',
            postgresql.HSTORE(text_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            'sayname_translations',
            postgresql.HSTORE(text_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column('phoneNumber', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('nationality', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('country', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('city', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column(
            'awakeAvatarUrl',
            say.orm.types.ResourceURL(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            'sleptAvatarUrl',
            say.orm.types.ResourceURL(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column('gender', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column(
            'bio_translations',
            postgresql.HSTORE(text_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            'bio_summary_translations',
            postgresql.HSTORE(text_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column('sayFamilyCount', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column(
            'voiceUrl',
            say.orm.types.ResourceURL(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column('birthPlace', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('birthDate', sa.Date(), autoincrement=False, nullable=True),
        sa.Column('address', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('housingStatus', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('familyCount', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('education', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('status', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('existence_status', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('isDeleted', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('isConfirmed', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('confirmUser', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('confirmDate', sa.Date(), autoincrement=False, nullable=True),
        sa.Column('generatedCode', sa.String(), autoincrement=False, nullable=True),
        sa.Column('isMigrated', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('migratedId', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('migrateDate', sa.Date(), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id', name=op.f('child_version_pkey')),
    )
    op.create_index(
        op.f('child_version_end_transaction_id_idx'),
        'child_version',
        ['end_transaction_id'],
        unique=False,
    )
    op.create_index(
        op.f('child_version_existence_status_idx'),
        'child_version',
        ['existence_status'],
        unique=False,
    )
    op.create_index(
        op.f('child_version_generatedCode_idx'),
        'child_version',
        ['generatedCode'],
        unique=False,
    )
    op.create_index(
        op.f('child_version_id_ngo_idx'), 'child_version', ['id_ngo'], unique=False
    )
    op.create_index(
        op.f('child_version_id_social_worker_idx'),
        'child_version',
        ['id_social_worker'],
        unique=False,
    )
    op.create_index(
        op.f('child_version_isDeleted_idx'), 'child_version', ['isDeleted'], unique=False
    )
    op.create_index(
        op.f('child_version_isMigrated_idx'),
        'child_version',
        ['isMigrated'],
        unique=False,
    )
    op.create_index(
        op.f('child_version_migratedId_idx'),
        'child_version',
        ['migratedId'],
        unique=False,
    )
    op.create_index(
        op.f('child_version_operation_type_idx'),
        'child_version',
        ['operation_type'],
        unique=False,
    )
    op.create_index(
        op.f('child_version_transaction_id_idx'),
        'child_version',
        ['transaction_id'],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('child_version_transaction_id_idx'), table_name='child_version')
    op.drop_index(op.f('child_version_operation_type_idx'), table_name='child_version')
    op.drop_index(op.f('child_version_migratedId_idx'), table_name='child_version')
    op.drop_index(op.f('child_version_isMigrated_idx'), table_name='child_version')
    op.drop_index(op.f('child_version_isDeleted_idx'), table_name='child_version')
    op.drop_index(op.f('child_version_id_social_worker_idx'), table_name='child_version')
    op.drop_index(op.f('child_version_id_ngo_idx'), table_name='child_version')
    op.drop_index(op.f('child_version_generatedCode_idx'), table_name='child_version')
    op.drop_index(op.f('child_version_existence_status_idx'), table_name='child_version')
    op.drop_index(
        op.f('child_version_end_transaction_id_idx'), table_name='child_version'
    )
    op.drop_table('child_version')
    # ### end Alembic commands ###
