"""Init extensions and tracking sequence.

Revision ID: 0001
Revises: None
Create Date: 2026-04-26
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.execute("CREATE SEQUENCE IF NOT EXISTS bill_tracking_seq START 1 CACHE 50")


def downgrade() -> None:
    op.execute("DROP SEQUENCE IF EXISTS bill_tracking_seq")
    # Extensions are shared; don't drop them in downgrade
