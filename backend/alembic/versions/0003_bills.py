"""Create bills, bill_content_lines, bill_status_events tables.

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-26
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- bills ---
    op.create_table(
        "bills",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("tracking_number", sa.Text, unique=True, nullable=False),
        sa.Column("customer_code", sa.Text, nullable=True),
        sa.Column("customer_id", sa.BigInteger, sa.ForeignKey("customers.id"), nullable=True),
        # Sender snapshot
        sa.Column("sender_name", sa.Text, nullable=False),
        sa.Column("sender_address", sa.Text, nullable=False),
        sa.Column("sender_district", sa.Text, nullable=False),
        sa.Column("sender_province", sa.Text, nullable=False),
        sa.Column("sender_phone", sa.Text, nullable=False),
        # Receiver snapshot
        sa.Column("receiver_name", sa.Text, nullable=False),
        sa.Column("receiver_address", sa.Text, nullable=False),
        sa.Column("receiver_district", sa.Text, nullable=False),
        sa.Column("receiver_province", sa.Text, nullable=False),
        sa.Column("receiver_phone", sa.Text, nullable=False),
        # Service
        sa.Column("cargo_type", sa.Text, nullable=False),
        sa.Column(
            "service_tier_code",
            sa.Text,
            sa.ForeignKey("service_tiers.code"),
            nullable=False,
        ),
        # Fees (VND)
        sa.Column("fee_main", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("fee_fuel_surcharge", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("fee_other_surcharge", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("fee_vat", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("fee_total", sa.Numeric(14, 2), nullable=False),
        # Payer
        sa.Column("payer", sa.Text, nullable=False),
        # Lifecycle
        sa.Column("status", sa.Text, nullable=False, server_default="da_tao"),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_to_name", sa.Text, nullable=True),
        sa.Column("cancellation_reason", sa.Text, nullable=True),
        # Audit
        sa.Column("created_by", sa.BigInteger, sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("updated_by", sa.BigInteger, sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("print_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_printed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_printed_by", sa.BigInteger, sa.ForeignKey("users.id"), nullable=True),
        # CHECK constraints
        sa.CheckConstraint(
            "fee_total = fee_main + fee_fuel_surcharge + fee_other_surcharge + fee_vat",
            name="ck_bills_fee_total",
        ),
        sa.CheckConstraint(
            "status <> 'huy' OR cancellation_reason IS NOT NULL",
            name="ck_bills_cancel_reason",
        ),
        sa.CheckConstraint(
            "status <> 'da_giao' OR delivered_at IS NOT NULL",
            name="ck_bills_delivered_at",
        ),
        sa.CheckConstraint(
            "cargo_type IN ('document', 'goods')",
            name="ck_bills_cargo_type",
        ),
        sa.CheckConstraint(
            "payer IN ('sender', 'receiver')",
            name="ck_bills_payer",
        ),
        sa.CheckConstraint(
            "status IN ('da_tao', 'da_lay_hang', 'dang_van_chuyen', 'da_giao', 'hoan_tra', 'huy')",
            name="ck_bills_status",
        ),
    )

    # Indexes
    op.create_index("idx_bills_status_created_at", "bills", ["status", sa.text("created_at DESC")])
    op.create_index("idx_bills_sender_phone", "bills", ["sender_phone"])
    op.create_index("idx_bills_receiver_phone", "bills", ["receiver_phone"])
    op.create_index("idx_bills_customer_code", "bills", ["customer_code"])

    # GIN trigram indexes for diacritic-insensitive search
    op.execute(
        "CREATE INDEX idx_bills_search_sender_name ON bills "
        "USING GIN (unaccent(lower(sender_name)) gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX idx_bills_search_receiver_name ON bills "
        "USING GIN (unaccent(lower(receiver_name)) gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX idx_bills_search_sender_address ON bills "
        "USING GIN (unaccent(lower(sender_address)) gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX idx_bills_search_receiver_address ON bills "
        "USING GIN (unaccent(lower(receiver_address)) gin_trgm_ops)"
    )

    # --- bill_content_lines ---
    op.create_table(
        "bill_content_lines",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "bill_id",
            sa.BigInteger,
            sa.ForeignKey("bills.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("line_no", sa.Integer, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("weight_kg", sa.Numeric(12, 3), nullable=False),
        sa.Column("length_cm", sa.Numeric(8, 2), nullable=True),
        sa.Column("width_cm", sa.Numeric(8, 2), nullable=True),
        sa.Column("height_cm", sa.Numeric(8, 2), nullable=True),
        sa.UniqueConstraint("bill_id", "line_no", name="uq_bill_content_lines_bill_line"),
        sa.CheckConstraint("quantity > 0", name="ck_bill_content_lines_qty"),
        sa.CheckConstraint("weight_kg >= 0", name="ck_bill_content_lines_weight"),
    )

    # --- bill_status_events ---
    op.create_table(
        "bill_status_events",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "bill_id",
            sa.BigInteger,
            sa.ForeignKey("bills.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("from_status", sa.Text, nullable=True),
        sa.Column("to_status", sa.Text, nullable=False),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("actor_id", sa.BigInteger, sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "idx_bill_status_events_bill",
        "bill_status_events",
        ["bill_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_table("bill_status_events")
    op.drop_table("bill_content_lines")
    op.drop_index("idx_bills_search_receiver_address", table_name="bills")
    op.drop_index("idx_bills_search_sender_address", table_name="bills")
    op.drop_index("idx_bills_search_receiver_name", table_name="bills")
    op.drop_index("idx_bills_search_sender_name", table_name="bills")
    op.drop_index("idx_bills_customer_code", table_name="bills")
    op.drop_index("idx_bills_receiver_phone", table_name="bills")
    op.drop_index("idx_bills_sender_phone", table_name="bills")
    op.drop_index("idx_bills_status_created_at", table_name="bills")
    op.drop_table("bills")
