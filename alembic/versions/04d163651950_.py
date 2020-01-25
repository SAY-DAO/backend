"""empty message

Revision ID: 04d163651950
Revises: 577a9b1b8182
Create Date: 2020-01-07 22:10:19.317625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04d163651950'
down_revision = '577a9b1b8182'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('child', 'bio')
    op.drop_column('child', 'bio_fa')
    op.drop_column('child', 'bioSummary_fa')
    op.drop_column('child', 'sayName')
    op.drop_column('child', 'bioSummary')
    op.drop_column('child', 'sayName_fa')
    op.drop_column('need', 'descriptionSummary')
    op.drop_column('need', 'name_fa')
    op.drop_column('need', 'name')
    op.drop_column('need', 'descriptionSummary_fa')
    op.drop_column('need', 'description')
    op.drop_column('need', 'description_fa')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('need', sa.Column('description_fa', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('need', sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('need', sa.Column('descriptionSummary_fa', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('need', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('need', sa.Column('name_fa', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('need', sa.Column('descriptionSummary', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('child', sa.Column('sayName_fa', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('child', sa.Column('bioSummary', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('child', sa.Column('sayName', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('child', sa.Column('bioSummary_fa', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('child', sa.Column('bio_fa', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('child', sa.Column('bio', sa.TEXT(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
