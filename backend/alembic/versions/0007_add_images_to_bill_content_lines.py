"""add images to bill_content_lines and make service_tier_code nullable

Revision ID: 0007
Revises: 0006
Create Date: 2026-09-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Images per content line (list of S3 keys)
    op.add_column(
        "bill_content_lines",
        sa.Column(
            "images",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    # Service tier is optional (form no longer requires it)
    op.alter_column(
        "bills",
        "service_tier_code",
        existing_type=sa.String(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "bills",
        "service_tier_code",
        existing_type=sa.String(),
        nullable=False,
    )
    op.drop_column("bill_content_lines", "images")
