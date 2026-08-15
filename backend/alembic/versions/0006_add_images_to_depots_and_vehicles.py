"""add images column to depots and vehicles

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-15 22:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0006'
down_revision: Union[str, None] = '0005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add images JSONB column with server_default='[]' to depots
    op.add_column(
        'depots',
        sa.Column(
            'images',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    # Add images JSONB column with server_default='[]' to vehicles
    op.add_column(
        'vehicles',
        sa.Column(
            'images',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column('vehicles', 'images')
    op.drop_column('depots', 'images')
