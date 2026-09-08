"""add cargo_type to bill_content_lines

Revision ID: 0008
Revises: 0007
Create Date: 2026-09-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "bill_content_lines",
        sa.Column("cargo_type", sa.String(), nullable=False, server_default="goods"),
    )


def downgrade() -> None:
    op.drop_column("bill_content_lines", "cargo_type")
