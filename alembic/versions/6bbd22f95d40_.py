"""empty message

Revision ID: 6bbd22f95d40
Revises: 426b0e45efee
Create Date: 2021-04-25 15:24:51.108523

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '6bbd22f95d40'
down_revision = '426b0e45efee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('child_id_ngo_idx'), 'child', ['id_ngo'], unique=False)
    op.create_index(op.f('child_id_social_worker_idx'), 'child', ['id_social_worker'], unique=False)
    op.create_index(op.f('need_child_id_idx'), 'need', ['child_id'], unique=False)
    op.create_index(op.f('need_family_id_family_idx'), 'need_family', ['id_family'], unique=False)
    op.create_index(op.f('need_family_id_need_idx'), 'need_family', ['id_need'], unique=False)
    op.create_index(op.f('need_family_id_user_idx'), 'need_family', ['id_user'], unique=False)
    op.create_index(op.f('need_receipt_need_id_idx'), 'need_receipt', ['need_id'], unique=False)
    op.create_index(op.f('need_receipt_receipt_id_idx'), 'need_receipt', ['receipt_id'], unique=False)
    op.create_index(op.f('need_receipt_sw_id_idx'), 'need_receipt', ['sw_id'], unique=False)
    op.create_index(op.f('payment_id_need_idx'), 'payment', ['id_need'], unique=False)
    op.create_index(op.f('payment_id_user_idx'), 'payment', ['id_user'], unique=False)
    op.create_index(op.f('receipt_owner_id_idx'), 'receipt', ['owner_id'], unique=False)
    op.create_index(op.f('reset_password_user_id_idx'), 'reset_password', ['user_id'], unique=False)
    op.create_index(op.f('social_worker_id_ngo_idx'), 'social_worker', ['id_ngo'], unique=False)
    op.create_index(op.f('social_worker_id_type_idx'), 'social_worker', ['id_type'], unique=False)
    op.create_index(op.f('user_family_id_family_idx'), 'user_family', ['id_family'], unique=False)
    op.create_index(op.f('user_family_id_user_idx'), 'user_family', ['id_user'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('user_family_id_user_idx'), table_name='user_family')
    op.drop_index(op.f('user_family_id_family_idx'), table_name='user_family')
    op.drop_index(op.f('social_worker_id_type_idx'), table_name='social_worker')
    op.drop_index(op.f('social_worker_id_ngo_idx'), table_name='social_worker')
    op.drop_index(op.f('reset_password_user_id_idx'), table_name='reset_password')
    op.drop_index(op.f('receipt_owner_id_idx'), table_name='receipt')
    op.drop_index(op.f('payment_id_user_idx'), table_name='payment')
    op.drop_index(op.f('payment_id_need_idx'), table_name='payment')
    op.drop_index(op.f('need_receipt_sw_id_idx'), table_name='need_receipt')
    op.drop_index(op.f('need_receipt_receipt_id_idx'), table_name='need_receipt')
    op.drop_index(op.f('need_receipt_need_id_idx'), table_name='need_receipt')
    op.drop_index(op.f('need_family_id_user_idx'), table_name='need_family')
    op.drop_index(op.f('need_family_id_need_idx'), table_name='need_family')
    op.drop_index(op.f('need_family_id_family_idx'), table_name='need_family')
    op.drop_index(op.f('need_child_id_idx'), table_name='need')
    op.drop_index(op.f('family_id_child_idx'), table_name='family')
    op.drop_index(op.f('child_id_social_worker_idx'), table_name='child')
    op.drop_index(op.f('child_id_ngo_idx'), table_name='child')
    # ### end Alembic commands ###