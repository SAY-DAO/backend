"""empty message

Revision ID: 7b988b91284f
Revises: a28ee7394da4
Create Date: 2020-02-04 01:12:47.146605

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


# revision identifiers, used by Alembic.
revision = '7b988b91284f'
down_revision = 'a28ee7394da4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('DROP TABLE core_organization CASCADE;')
    op.drop_index('idx_fieldvalues_field_id', table_name='metabase_fieldvalues')
    op.drop_table('metabase_fieldvalues')
    op.drop_index('idx_cardfavorite_card_id', table_name='report_cardfavorite')
    op.drop_index('idx_cardfavorite_owner_id', table_name='report_cardfavorite')
    op.drop_table('report_cardfavorite')
    op.drop_index('idx_permissionsviolation_user_id', table_name='core_permissionsviolation')
    op.drop_table('core_permissionsviolation')
    op.drop_index('idx_dashboard_creator_id', table_name='report_dashboard')
    op.drop_index('idx_dashboard_organization_id', table_name='report_dashboard')
    op.execute('DROP TABLE report_dashboard CASCADE;')
    op.drop_index('idx_emailreport_recipients_emailreport_id', table_name='report_emailreport_recipients')
    op.drop_index('idx_emailreport_recipients_user_id', table_name='report_emailreport_recipients')
    op.drop_table('report_emailreport_recipients')
    op.drop_index('idx_queryexecution_executor_id', table_name='query_queryexecution')
    op.drop_index('idx_queryexecution_query_id', table_name='query_queryexecution')
    op.drop_table('query_queryexecution')
    op.drop_index('idx_dashboardsubscription_dashboard_id', table_name='report_dashboardsubscription')
    op.drop_index('idx_dashboardsubscription_user_id', table_name='report_dashboardsubscription')
    op.drop_table('report_dashboardsubscription')
    op.execute('DROP TABLE core_session CASCADE;')
    op.execute('DROP TABLE databasechangeloglock CASCADE;')
    op.drop_index('idx_annotation_author_id', table_name='annotation_annotation')
    op.drop_index('idx_annotation_object_id', table_name='annotation_annotation')
    op.drop_index('idx_annotation_object_type_id', table_name='annotation_annotation')
    op.drop_index('idx_annotation_organization_id', table_name='annotation_annotation')
    op.execute('DROP TABLE annotation_annotation CASCADE;')
    op.drop_index('idx_foreignkey_destination_id', table_name='metabase_foreignkey')
    op.drop_index('idx_foreignkey_origin_id', table_name='metabase_foreignkey')
    op.execute('DROP TABLE metabase_foreignkey CASCADE;')
    op.drop_index('idx_userorgperm_organization_id', table_name='core_userorgperm')
    op.drop_index('idx_userorgperm_user_id', table_name='core_userorgperm')
    op.execute('DROP TABLE core_userorgperm CASCADE;')
    op.execute('DROP TABLE databasechangelog CASCADE;')
    op.drop_index('idx_table_db_id', table_name='metabase_table')
    op.execute('DROP TABLE metabase_table CASCADE;')
    op.drop_index('idx_query_creator_id', table_name='query_query')
    op.drop_index('idx_query_database_id', table_name='query_query')
    op.execute('DROP TABLE query_query CASCADE;')
    op.drop_index('idx_revision_model_model_id', table_name='revision')
    op.execute('DROP TABLE revision CASCADE;')
    op.drop_index('idx_card_creator_id', table_name='report_card')
    op.drop_index('idx_card_organization_id', table_name='report_card')
    op.execute('DROP TABLE report_card CASCADE;')
    op.execute('DROP TABLE setting CASCADE;')
    op.drop_index('idx_database_organization_id', table_name='metabase_database')
    op.execute('DROP TABLE metabase_database CASCADE;')
    op.drop_index('idx_tablesegment_table_id', table_name='metabase_tablesegment')
    op.execute('DROP TABLE metabase_tablesegment CASCADE;')
    op.drop_index('idx_dashboardcard_card_id', table_name='report_dashboardcard')
    op.drop_index('idx_dashboardcard_dashboard_id', table_name='report_dashboardcard')
    op.execute('DROP TABLE report_dashboardcard CASCADE;')
    op.drop_index('idx_emailreportexecutions_organization_id', table_name='report_emailreportexecutions')
    op.drop_index('idx_emailreportexecutions_report_id', table_name='report_emailreportexecutions')
    op.execute('DROP TABLE report_emailreportexecutions CASCADE;')
    op.execute('DROP TABLE core_user CASCADE;')
    op.drop_index('idx_field_table_id', table_name='metabase_field')
    op.execute('DROP TABLE metabase_field CASCADE;')
    op.drop_index('idx_emailreport_creator_id', table_name='report_emailreport')
    op.drop_index('idx_emailreport_organization_id', table_name='report_emailreport')
    op.execute('DROP TABLE report_emailreport CASCADE;')

    op.add_column('need', sa.Column('purchase_cost', sa.Integer(), nullable=True))
    op.alter_column('need_family', 'paid',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_server_default=sa.text('0'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('need_family', 'paid',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('0'))
    op.drop_column('need', 'purchase_cost')
    op.create_table('report_emailreport',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('report_emailreport_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('public_perms', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('mode', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('version', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('dataset_query', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('email_addresses', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('creator_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('organization_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('schedule', sa.TEXT(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['creator_id'], ['core_user.id'], name='fk_emailreport_ref_user_id'),
    sa.PrimaryKeyConstraint('id', name='report_emailreport_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('idx_emailreport_organization_id', 'report_emailreport', ['organization_id'], unique=False)
    op.create_index('idx_emailreport_creator_id', 'report_emailreport', ['creator_id'], unique=False)
    op.create_table('metabase_field',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('metabase_field_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('base_type', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('special_type', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('active', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('preview_display', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('position', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('table_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('field_type', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('parent_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('display_name', sa.VARCHAR(length=254), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['metabase_field.id'], name='fk_field_parent_ref_field_id'),
    sa.ForeignKeyConstraint(['table_id'], ['metabase_table.id'], name='fk_field_ref_table_id'),
    sa.PrimaryKeyConstraint('id', name='metabase_field_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('idx_field_table_id', 'metabase_field', ['table_id'], unique=False)
    op.create_table('core_user',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('core_user_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('email', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('first_name', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('last_name', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('password', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('password_salt', sa.VARCHAR(length=254), server_default=sa.text("'default'::character varying"), autoincrement=False, nullable=False),
    sa.Column('date_joined', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('last_login', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('is_staff', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('is_superuser', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('reset_token', sa.VARCHAR(length=254), autoincrement=False, nullable=True),
    sa.Column('reset_triggered', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='core_user_pkey'),
    sa.UniqueConstraint('email', name='core_user_email_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('report_emailreportexecutions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('details', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('started_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('finished_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('error', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('sent_email', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('organization_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('report_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['report_id'], ['report_emailreport.id'], name='fk_emailreportexecutions_ref_report_id'),
    sa.PrimaryKeyConstraint('id', name='report_emailreportexecutions_pkey')
    )
    op.create_index('idx_emailreportexecutions_report_id', 'report_emailreportexecutions', ['report_id'], unique=False)
    op.create_index('idx_emailreportexecutions_organization_id', 'report_emailreportexecutions', ['organization_id'], unique=False)
    op.create_table('report_dashboardcard',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('sizeX', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('sizeY', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('row', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('col', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('card_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('dashboard_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['card_id'], ['report_card.id'], name='fk_dashboardcard_ref_card_id'),
    sa.ForeignKeyConstraint(['dashboard_id'], ['report_dashboard.id'], name='fk_dashboardcard_ref_dashboard_id'),
    sa.PrimaryKeyConstraint('id', name='report_dashboardcard_pkey')
    )
    op.create_index('idx_dashboardcard_dashboard_id', 'report_dashboardcard', ['dashboard_id'], unique=False)
    op.create_index('idx_dashboardcard_card_id', 'report_dashboardcard', ['card_id'], unique=False)
    op.create_table('metabase_tablesegment',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('table_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('filter_clause', sa.TEXT(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['table_id'], ['metabase_table.id'], name='fk_tablesegment_ref_table_id'),
    sa.PrimaryKeyConstraint('id', name='metabase_tablesegment_pkey')
    )
    op.create_index('idx_tablesegment_table_id', 'metabase_tablesegment', ['table_id'], unique=False)
    op.create_table('metabase_database',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('metabase_database_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('organization_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('details', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('engine', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='metabase_database_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('idx_database_organization_id', 'metabase_database', ['organization_id'], unique=False)
    op.create_table('setting',
    sa.Column('key', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('value', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('key', name='setting_pkey')
    )
    op.create_table('report_card',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('report_card_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('display', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('public_perms', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('dataset_query', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('visualization_settings', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('creator_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('organization_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('database_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('table_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('query_type', sa.VARCHAR(length=16), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['core_user.id'], name='fk_card_ref_user_id'),
    sa.ForeignKeyConstraint(['database_id'], ['metabase_database.id'], name='fk_report_card_ref_database_id'),
    sa.ForeignKeyConstraint(['table_id'], ['metabase_table.id'], name='fk_report_card_ref_table_id'),
    sa.PrimaryKeyConstraint('id', name='report_card_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('idx_card_organization_id', 'report_card', ['organization_id'], unique=False)
    op.create_index('idx_card_creator_id', 'report_card', ['creator_id'], unique=False)
    op.create_table('revision',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('model', sa.VARCHAR(length=16), autoincrement=False, nullable=False),
    sa.Column('model_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('object', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('is_reversion', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['core_user.id'], name='fk_revision_ref_user_id'),
    sa.PrimaryKeyConstraint('id', name='revision_pkey')
    )
    op.create_index('idx_revision_model_model_id', 'revision', ['model', 'model_id'], unique=False)
    op.create_table('query_query',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('query_query_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('type', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('details', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('version', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('public_perms', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('creator_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('database_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['creator_id'], ['core_user.id'], name='fk_query_ref_user_id'),
    sa.ForeignKeyConstraint(['database_id'], ['metabase_database.id'], name='fk_query_ref_database_id'),
    sa.PrimaryKeyConstraint('id', name='query_query_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('idx_query_database_id', 'query_query', ['database_id'], unique=False)
    op.create_index('idx_query_creator_id', 'query_query', ['creator_id'], unique=False)
    op.create_table('metabase_table',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('metabase_table_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('rows', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('entity_name', sa.VARCHAR(length=254), autoincrement=False, nullable=True),
    sa.Column('entity_type', sa.VARCHAR(length=254), autoincrement=False, nullable=True),
    sa.Column('active', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('db_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('display_name', sa.VARCHAR(length=254), autoincrement=False, nullable=True),
    sa.Column('visibility_type', sa.VARCHAR(length=254), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['db_id'], ['metabase_database.id'], name='fk_table_ref_database_id'),
    sa.PrimaryKeyConstraint('id', name='metabase_table_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('idx_table_db_id', 'metabase_table', ['db_id'], unique=False)
    op.create_table('databasechangelog',
    sa.Column('id', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('author', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('filename', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('dateexecuted', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('orderexecuted', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('exectype', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('md5sum', sa.VARCHAR(length=35), autoincrement=False, nullable=True),
    sa.Column('description', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('comments', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('tag', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('liquibase', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('contexts', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('labels', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('deployment_id', sa.VARCHAR(length=10), autoincrement=False, nullable=True)
    )
    op.create_table('core_userorgperm',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('admin', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('organization_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['core_organization.id'], name='fk_userorgperm_ref_organization_id'),
    sa.ForeignKeyConstraint(['user_id'], ['core_user.id'], name='fk_userorgperm_ref_user_id'),
    sa.PrimaryKeyConstraint('id', name='core_userorgperm_pkey'),
    sa.UniqueConstraint('user_id', 'organization_id', name='idx_unique_user_id_organization_id')
    )
    op.create_index('idx_userorgperm_user_id', 'core_userorgperm', ['user_id'], unique=False)
    op.create_index('idx_userorgperm_organization_id', 'core_userorgperm', ['organization_id'], unique=False)
    op.create_table('metabase_foreignkey',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('relationship', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('destination_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('origin_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['destination_id'], ['metabase_field.id'], name='fk_foreignkey_dest_ref_field_id'),
    sa.ForeignKeyConstraint(['origin_id'], ['metabase_field.id'], name='fk_foreignkey_origin_ref_field_id'),
    sa.PrimaryKeyConstraint('id', name='metabase_foreignkey_pkey')
    )
    op.create_index('idx_foreignkey_origin_id', 'metabase_foreignkey', ['origin_id'], unique=False)
    op.create_index('idx_foreignkey_destination_id', 'metabase_foreignkey', ['destination_id'], unique=False)
    op.create_table('annotation_annotation',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('start', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('end', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('title', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('body', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('annotation_type', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('edit_count', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('object_type_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('object_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('author_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('organization_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['core_user.id'], name='fk_annotation_ref_user_id'),
    sa.PrimaryKeyConstraint('id', name='annotation_annotation_pkey')
    )
    op.create_index('idx_annotation_organization_id', 'annotation_annotation', ['organization_id'], unique=False)
    op.create_index('idx_annotation_object_type_id', 'annotation_annotation', ['object_type_id'], unique=False)
    op.create_index('idx_annotation_object_id', 'annotation_annotation', ['object_id'], unique=False)
    op.create_index('idx_annotation_author_id', 'annotation_annotation', ['author_id'], unique=False)
    op.create_table('databasechangeloglock',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('locked', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('lockgranted', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('lockedby', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='databasechangeloglock_pkey')
    )
    op.create_table('core_session',
    sa.Column('id', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['core_user.id'], name='fk_session_ref_user_id'),
    sa.PrimaryKeyConstraint('id', name='core_session_pkey')
    )
    op.create_table('report_dashboardsubscription',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('dashboard_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['dashboard_id'], ['report_dashboard.id'], name='fk_dashboardsubscription_ref_dashboard_id'),
    sa.ForeignKeyConstraint(['user_id'], ['core_user.id'], name='fk_dashboardsubscription_ref_user_id'),
    sa.PrimaryKeyConstraint('id', name='report_dashboardsubscription_pkey'),
    sa.UniqueConstraint('dashboard_id', 'user_id', name='idx_uniq_dashsubscrip_dashboard_id_user_id')
    )
    op.create_index('idx_dashboardsubscription_user_id', 'report_dashboardsubscription', ['user_id'], unique=False)
    op.create_index('idx_dashboardsubscription_dashboard_id', 'report_dashboardsubscription', ['dashboard_id'], unique=False)
    op.create_table('query_queryexecution',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('uuid', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('version', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('json_query', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('raw_query', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('started_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('finished_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('running_time', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('error', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('result_file', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('result_rows', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('result_data', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('query_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('additional_info', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('executor_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['executor_id'], ['core_user.id'], name='fk_queryexecution_ref_user_id'),
    sa.ForeignKeyConstraint(['query_id'], ['query_query.id'], name='fk_queryexecution_ref_query_id'),
    sa.PrimaryKeyConstraint('id', name='query_queryexecution_pkey'),
    sa.UniqueConstraint('uuid', name='query_queryexecution_uuid_key')
    )
    op.create_index('idx_queryexecution_query_id', 'query_queryexecution', ['query_id'], unique=False)
    op.create_index('idx_queryexecution_executor_id', 'query_queryexecution', ['executor_id'], unique=False)
    op.create_table('report_emailreport_recipients',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('emailreport_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['emailreport_id'], ['report_emailreport.id'], name='fk_emailreport_recipients_ref_emailreport_id'),
    sa.ForeignKeyConstraint(['user_id'], ['core_user.id'], name='fk_emailreport_recipients_ref_user_id'),
    sa.PrimaryKeyConstraint('id', name='report_emailreport_recipients_pkey'),
    sa.UniqueConstraint('emailreport_id', 'user_id', name='idx_uniq_emailreportrecip_emailreport_id_user_id')
    )
    op.create_index('idx_emailreport_recipients_user_id', 'report_emailreport_recipients', ['user_id'], unique=False)
    op.create_index('idx_emailreport_recipients_emailreport_id', 'report_emailreport_recipients', ['emailreport_id'], unique=False)
    op.create_table('report_dashboard',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('public_perms', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('creator_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('organization_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['core_user.id'], name='fk_dashboard_ref_user_id'),
    sa.PrimaryKeyConstraint('id', name='report_dashboard_pkey')
    )
    op.create_index('idx_dashboard_organization_id', 'report_dashboard', ['organization_id'], unique=False)
    op.create_index('idx_dashboard_creator_id', 'report_dashboard', ['creator_id'], unique=False)
    op.create_table('core_permissionsviolation',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('url', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['core_user.id'], name='fk_permissionviolation_ref_user_id'),
    sa.PrimaryKeyConstraint('id', name='core_permissionsviolation_pkey')
    )
    op.create_index('idx_permissionsviolation_user_id', 'core_permissionsviolation', ['user_id'], unique=False)
    op.create_table('report_cardfavorite',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('card_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['card_id'], ['report_card.id'], name='fk_cardfavorite_ref_card_id'),
    sa.ForeignKeyConstraint(['owner_id'], ['core_user.id'], name='fk_cardfavorite_ref_user_id'),
    sa.PrimaryKeyConstraint('id', name='report_cardfavorite_pkey'),
    sa.UniqueConstraint('card_id', 'owner_id', name='idx_unique_cardfavorite_card_id_owner_id')
    )
    op.create_index('idx_cardfavorite_owner_id', 'report_cardfavorite', ['owner_id'], unique=False)
    op.create_index('idx_cardfavorite_card_id', 'report_cardfavorite', ['card_id'], unique=False)
    op.create_table('metabase_fieldvalues',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('values', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('human_readable_values', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('field_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['field_id'], ['metabase_field.id'], name='fk_fieldvalues_ref_field_id'),
    sa.PrimaryKeyConstraint('id', name='metabase_fieldvalues_pkey')
    )
    op.create_index('idx_fieldvalues_field_id', 'metabase_fieldvalues', ['field_id'], unique=False)
    op.create_table('core_organization',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('slug', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('logo_url', sa.VARCHAR(length=254), autoincrement=False, nullable=True),
    sa.Column('inherits', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('report_timezone', sa.VARCHAR(length=254), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='core_organization_pkey'),
    sa.UniqueConstraint('slug', name='core_organization_slug_key')
    )
    # ### end Alembic commands ###
