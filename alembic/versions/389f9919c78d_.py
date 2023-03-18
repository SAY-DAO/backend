"""empty message

Revision ID: 389f9919c78d
Revises: e71c915653f6
Create Date: 2022-11-07 23:24:58.623154

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '389f9919c78d'
down_revision = 'e71c915653f6'
branch_labels = None
depends_on = None


def upgrade():
    from say.models import Child
    from say.orm import init_model
    from say.orm import session

    init_model(op.get_bind())

    op.alter_column('child', 'birthPlace', nullable=True, new_column_name='_birthPlace')
    op.alter_column('child', 'city', nullable=True, new_column_name='_city')
    op.alter_column('child', 'country', nullable=True, new_column_name='_country')
    op.alter_column('child', 'nationality', nullable=True, new_column_name='_nationality')

    op.add_column('child', sa.Column('birth_place_id', sa.Integer(), nullable=True))
    op.add_column('child', sa.Column('city_id', sa.Integer(), nullable=True))
    op.add_column('child', sa.Column('nationality_id', sa.Integer(), nullable=True))

    op.create_foreign_key(
        op.f('child_birth_place_id_cities_fkey'),
        'child',
        'cities',
        ['birth_place_id'],
        ['id'],
    )
    op.create_foreign_key(
        op.f('child_city_id_cities_fkey'), 'child', 'cities', ['city_id'], ['id']
    )
    op.create_foreign_key(
        op.f('child_nationality_id_countries_fkey'),
        'child',
        'countries',
        ['nationality_id'],
        ['id'],
    )

    op.alter_column(
        'child_version', 'birthPlace', nullable=True, new_column_name='_birthPlace'
    )
    op.alter_column('child_version', 'city', nullable=True, new_column_name='_city')
    op.alter_column('child_version', 'country', nullable=True, new_column_name='_country')
    op.alter_column(
        'child_version', 'nationality', nullable=True, new_column_name='_nationality'
    )
    op.alter_column(
        'child_version',
        'birthPlace_mod',
        nullable=True,
        new_column_name='_birthPlace_mod',
    )
    op.alter_column(
        'child_version', 'city_mod', nullable=True, new_column_name='_city_mod'
    )
    op.alter_column(
        'child_version', 'country_mod', nullable=True, new_column_name='_country_mod'
    )
    op.alter_column(
        'child_version',
        'nationality_mod',
        nullable=True,
        new_column_name='_nationality_mod',
    )

    op.add_column(
        'child_version',
        sa.Column('birth_place_id', sa.Integer(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'child_version',
        sa.Column(
            'birth_place_id_mod',
            sa.Boolean(),
            server_default=sa.text('false'),
            nullable=False,
        ),
    )
    op.add_column(
        'child_version',
        sa.Column('city_id', sa.Integer(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'child_version',
        sa.Column(
            'city_id_mod', sa.Boolean(), server_default=sa.text('false'), nullable=False
        ),
    )
    op.add_column(
        'child_version',
        sa.Column('nationality_id', sa.Integer(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'child_version',
        sa.Column(
            'nationality_id_mod',
            sa.Boolean(),
            server_default=sa.text('false'),
            nullable=False,
        ),
    )

    for child in session.query(Child):
        if child._city == 1:
            child.city_id = 135129  # tehran
        else:
            child.city_id = 134664  # Karaj

        if child._nationality == '93':
            child.nationality_id = 1  # Afghanistan
        else:
            child.nationality_id = 103  # Iran

        if child._birthPlace in ['Afghanistan', 'افغنستان']:
            child.birth_place_id = 79  # Kabul
        elif child._birthPlace == 'تربت جام':
            child.birth_place_id = 135131  # Torbat e jaam
        elif child._birthPlace in ['Iran', 'Tehran']:
            child.birth_place_id = 135129  # Tehran
        else:
            child.birth_place_id = 134664  # Karaj

    session.commit()

    op.alter_column('user', '_city', existing_type=sa.INTEGER(), nullable=True)
    op.drop_column('user', 'birthPlace')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'user', sa.Column('birthPlace', sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.alter_column('user', '_city', existing_type=sa.INTEGER(), nullable=False)
    op.add_column(
        'child_version',
        sa.Column('birthPlace', sa.TEXT(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'child_version',
        sa.Column(
            'country_mod',
            sa.BOOLEAN(),
            server_default=sa.text('false'),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        'child_version',
        sa.Column('city', sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'child_version',
        sa.Column(
            'city_mod',
            sa.BOOLEAN(),
            server_default=sa.text('false'),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        'child_version',
        sa.Column('nationality', sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'child_version',
        sa.Column('country', sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'child_version',
        sa.Column(
            'birthPlace_mod',
            sa.BOOLEAN(),
            server_default=sa.text('false'),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        'child_version',
        sa.Column(
            'nationality_mod',
            sa.BOOLEAN(),
            server_default=sa.text('false'),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column('child_version', 'nationality_id_mod')
    op.drop_column('child_version', 'nationality_id')
    op.drop_column('child_version', 'city_id_mod')
    op.drop_column('child_version', 'city_id')
    op.drop_column('child_version', 'birth_place_id_mod')
    op.drop_column('child_version', 'birth_place_id')
    op.drop_column('child_version', '_nationality_mod')
    op.drop_column('child_version', '_nationality')
    op.drop_column('child_version', '_country_mod')
    op.drop_column('child_version', '_country')
    op.drop_column('child_version', '_city_mod')
    op.drop_column('child_version', '_city')
    op.drop_column('child_version', '_birthPlace_mod')
    op.drop_column('child_version', '_birthPlace')
    op.add_column(
        'child',
        sa.Column('nationality', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'child', sa.Column('city', sa.INTEGER(), autoincrement=False, nullable=False)
    )
    op.add_column(
        'child', sa.Column('birthPlace', sa.TEXT(), autoincrement=False, nullable=True)
    )
    op.add_column(
        'child', sa.Column('country', sa.INTEGER(), autoincrement=False, nullable=False)
    )
    op.drop_constraint(
        op.f('child_nationality_id_countries_fkey'), 'child', type_='foreignkey'
    )
    op.drop_constraint(op.f('child_city_id_cities_fkey'), 'child', type_='foreignkey')
    op.drop_constraint(
        op.f('child_birth_place_id_cities_fkey'), 'child', type_='foreignkey'
    )
    op.drop_column('child', 'nationality_id')
    op.drop_column('child', 'city_id')
    op.drop_column('child', 'birth_place_id')
    op.drop_column('child', '_nationality')
    op.drop_column('child', '_country')
    op.drop_column('child', '_city')
    op.drop_column('child', '_birthPlace')
    # ### end Alembic commands ###
