"""add immutable sender and receiver snapshots to bills

Revision ID: 0013
Revises: 0012
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0013"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("bills", sa.Column("sender_snapshot", postgresql.JSONB(), nullable=True))
    op.add_column("bills", sa.Column("receiver_snapshot", postgresql.JSONB(), nullable=True))
    # Backfill once; after this migration bill rendering never reads mutable customer fields.
    op.execute("""
        UPDATE bills b SET sender_snapshot = jsonb_build_object(
          'customer_id', s.id, 'name', s.name, 'phone', s.phone,
          'address_detail', s.metadata->>'address_detail', 'province_code', s.metadata->>'province_code',
          'province_name', s.metadata->>'province_name', 'ward_code', s.metadata->>'ward_code',
          'ward_name', s.metadata->>'ward_name')
        FROM customers s WHERE s.id = b.sender_id
    """)
    op.execute("""
        UPDATE bills b SET receiver_snapshot = jsonb_build_object(
          'customer_id', r.id, 'name', r.name, 'phone', r.phone,
          'address_detail', r.metadata->>'address_detail', 'province_code', r.metadata->>'province_code',
          'province_name', r.metadata->>'province_name', 'ward_code', r.metadata->>'ward_code',
          'ward_name', r.metadata->>'ward_name')
        FROM customers r WHERE r.id = b.receiver_id
    """)
    op.alter_column("bills", "sender_snapshot", nullable=False, server_default=sa.text("'{}'::jsonb"))
    op.alter_column("bills", "receiver_snapshot", nullable=False, server_default=sa.text("'{}'::jsonb"))


def downgrade() -> None:
    op.drop_column("bills", "receiver_snapshot")
    op.drop_column("bills", "sender_snapshot")
