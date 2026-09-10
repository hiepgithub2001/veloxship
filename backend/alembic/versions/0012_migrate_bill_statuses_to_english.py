"""migrate bill statuses to English lifecycle codes

Revision ID: 0012
Revises: 0011
Create Date: 2026-09-08

The Bill ORM was updated to use English lifecycle codes, but the original
database constraint and server default still used the legacy Vietnamese codes.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


LEGACY_TO_CURRENT = {
    "da_tao": "created",
    "da_lay_hang": "picked_up",
    "dang_van_chuyen": "in_transit",
    "da_giao": "delivered",
    "hoan_tra": "returned",
    "huy": "cancelled",
}


def upgrade() -> None:
    # The legacy constraint can have either name, depending on whether the
    # metadata naming convention was applied when the database was created.
    op.execute("ALTER TABLE bills DROP CONSTRAINT IF EXISTS ck_bills_status")
    op.execute("ALTER TABLE bills DROP CONSTRAINT IF EXISTS ck_bills_ck_bills_status")

    for legacy_status, current_status in LEGACY_TO_CURRENT.items():
        op.execute(
            sa.text("UPDATE bills SET status = :current WHERE status = :legacy").bindparams(
                current=current_status,
                legacy=legacy_status,
            )
        )

    op.alter_column(
        "bills",
        "status",
        existing_type=sa.String(),
        server_default="created",
    )
    op.create_check_constraint(
        op.f("ck_bills_ck_bills_status"),
        "bills",
        "status IN ('created', 'picked_up', 'in_transit', 'delivered', 'returned', 'cancelled')",
    )


def downgrade() -> None:
    op.drop_constraint(op.f("ck_bills_ck_bills_status"), "bills", type_="check")

    for legacy_status, current_status in LEGACY_TO_CURRENT.items():
        op.execute(
            sa.text("UPDATE bills SET status = :legacy WHERE status = :current").bindparams(
                current=current_status,
                legacy=legacy_status,
            )
        )

    op.alter_column(
        "bills",
        "status",
        existing_type=sa.String(),
        server_default="da_tao",
    )
    op.create_check_constraint(
        op.f("ck_bills_status"),
        "bills",
        "status IN ('da_tao', 'da_lay_hang', 'dang_van_chuyen', 'da_giao', 'hoan_tra', 'huy')",
    )
