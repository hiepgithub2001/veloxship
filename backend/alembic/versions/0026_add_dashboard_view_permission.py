"""grant dashboard:view to desk roles

The action is added to ``PERMISSION_CATALOG`` and ``ROLE_DEFAULT_PERMISSIONS``
in code, but permissions are **rows** in ``role_permissions`` (migration 0019),
so existing deployments need this migration to actually hand the action to the
roles that run the dashboard. ``admin`` bypasses every check and needs no row.

``shipper`` is deliberately excluded — bưu tá see the bill list instead.

Revision ID: 0026
Revises: 0025
Create Date: 2026-11-06
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0026"
down_revision: str | None = "0025"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ACTION = "dashboard:view"
TARGET_ROLES = ("operator", "depot_manager", "cashier", "accountant")


def upgrade() -> None:
    for role in TARGET_ROLES:
        op.execute(
            sa.text(
                "INSERT INTO role_permissions (role, action) VALUES (:role, :action) "
                "ON CONFLICT DO NOTHING"
            ).bindparams(role=role, action=ACTION)
        )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM role_permissions WHERE action = :action AND role IN "
            "('operator', 'depot_manager', 'cashier', 'accountant')"
        ).bindparams(action=ACTION)
    )
