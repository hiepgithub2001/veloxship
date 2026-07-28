"""drop districts and link wards directly to provinces

Revision ID: 0004_drop_districts
Revises: 8e6679d4b6ec
Create Date: 2026-07-28 16:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0004_drop_districts'
down_revision: Union[str, None] = '8e6679d4b6ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add province_code to wards
    op.add_column('wards', sa.Column('province_code', sa.String(), nullable=True))
    op.create_foreign_key(
        op.f('fk_wards_province_code_provinces'),
        'wards',
        'provinces',
        ['province_code'],
        ['code'],
    )

    # 2. Drop district foreign key and column from wards
    op.drop_constraint('fk_wards_district_code_districts', 'wards', type_='foreignkey')
    op.drop_column('wards', 'district_code')

    # Make province_code NOT NULL now that schema is migrated
    op.alter_column('wards', 'province_code', nullable=False)

    # 3. Drop districts table
    op.drop_table('districts')


def downgrade() -> None:
    # Re-create districts table
    op.create_table(
        'districts',
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('name_en', sa.Text(), nullable=True),
        sa.Column('province_code', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['province_code'], ['provinces.code'], name=op.f('fk_districts_province_code_provinces')),
        sa.PrimaryKeyConstraint('code', name=op.f('pk_districts'))
    )

    op.add_column('wards', sa.Column('district_code', sa.String(), nullable=True))
    op.create_foreign_key(
        op.f('fk_wards_district_code_districts'),
        'wards',
        'districts',
        ['district_code'],
        ['code'],
    )

    op.drop_constraint(op.f('fk_wards_province_code_provinces'), 'wards', type_='foreignkey')
    op.drop_column('wards', 'province_code')
