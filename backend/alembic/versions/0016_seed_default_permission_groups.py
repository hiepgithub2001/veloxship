"""seed default permission groups

Revision ID: 0016
Revises: 0015
Create Date: 2026-10-08

Idempotently seed the default permission groups (matching the legacy user
roles) so the permission-management screen is never empty. The admin account
is assigned to the "Admin hệ thống" group.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0016"
down_revision: Union[str, None] = "0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ALL_ACTIONS = [
    "bill:view", "bill:create", "bill:update", "bill:cancel",
    "bill:rollback", "bill:adjust_cod",
    "warehouse:inbound", "warehouse:outbound", "warehouse:bagging", "warehouse:audit",
    "customer:view", "customer:create", "customer:update", "customer:delete",
    "finance:cod_handover", "finance:cashier_confirm", "finance:ledger",
    "fleet:view", "fleet:manage",
    "depot:view", "depot:manage",
    "iam:view_users", "iam:manage_users", "iam:manage_permissions",
]

DEFAULT_GROUPS: list[tuple[str, str, list[str]]] = [
    ("Admin hệ thống", "Nhóm quyền mặc định cho vai trò admin", ALL_ACTIONS),
    (
        "Nhân viên quầy",
        "Nhóm quyền mặc định cho vai trò operator",
        [
            "bill:view", "bill:create", "bill:update",
            "customer:view", "customer:create", "customer:update",
            "warehouse:inbound", "warehouse:outbound",
        ],
    ),
    (
        "Thủ kho",
        "Nhóm quyền mặc định cho vai trò depot_manager",
        [
            "bill:view", "customer:view",
            "warehouse:inbound", "warehouse:outbound",
            "warehouse:bagging", "warehouse:audit",
        ],
    ),
    (
        "Thủ quỹ",
        "Nhóm quyền mặc định cho vai trò cashier",
        ["bill:view", "finance:cod_handover", "finance:cashier_confirm", "finance:ledger"],
    ),
    (
        "Kế toán",
        "Nhóm quyền mặc định cho vai trò accountant",
        [
            "bill:view", "customer:view",
            "finance:cod_handover", "finance:cashier_confirm", "finance:ledger",
        ],
    ),
    ("Bưu tá", "Nhóm quyền mặc định cho vai trò shipper", ["bill:view", "warehouse:outbound"]),
]


def upgrade() -> None:
    for name, description, actions in DEFAULT_GROUPS:
        op.execute(
            sa.text(
                "INSERT INTO permission_groups (name, description) "
                "VALUES (:name, :description) ON CONFLICT (name) DO NOTHING"
            ).bindparams(name=name, description=description)
        )
        for action in actions:
            op.execute(
                sa.text(
                    "INSERT INTO permission_actions (group_id, action) "
                    "SELECT id, :action FROM permission_groups WHERE name = :name "
                    "ON CONFLICT (group_id, action) DO NOTHING"
                ).bindparams(name=name, action=action)
            )

    # Assign the built-in admin account to the default admin group.
    op.execute(
        sa.text(
            "INSERT INTO user_permission_groups (user_id, group_id) "
            "SELECT u.id, g.id FROM users u, permission_groups g "
            "WHERE u.username = 'admin' AND g.name = 'Admin hệ thống' "
            "ON CONFLICT (user_id, group_id) DO NOTHING"
        )
    )


def downgrade() -> None:
    for name, _description, _actions in DEFAULT_GROUPS:
        op.execute(
            sa.text("DELETE FROM permission_groups WHERE name = :name").bindparams(name=name)
        )
