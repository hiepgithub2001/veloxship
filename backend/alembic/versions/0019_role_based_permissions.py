"""replace permission groups with dynamic roles + role_permissions

Revision ID: 0019
Revises: 0018
Create Date: 2026-10-08

Drops the permission-group indirection (permission_groups / permission_actions /
user_permission_groups) and replaces it with a direct role → action mapping:

  roles (dynamic, seeded with six defaults)
    ├── users.role        (FK → roles.code)
    └── role_permissions  (role, action) — which actions each role grants
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0019"
down_revision: Union[str, None] = "0018"
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

ROLES = [
    ("admin", "Quản trị viên"),
    ("operator", "Nhân viên quầy"),
    ("depot_manager", "Thủ kho"),
    ("cashier", "Thủ quỹ"),
    ("accountant", "Kế toán"),
    ("shipper", "Bưu tá"),
]

ROLE_PERMISSIONS = {
    "admin": sorted(ALL_ACTIONS),
    "operator": [
        "bill:view", "bill:create", "bill:update",
        "customer:view", "customer:create", "customer:update",
        "warehouse:inbound", "warehouse:outbound",
    ],
    "depot_manager": [
        "bill:view",
        "customer:view",
        "warehouse:inbound", "warehouse:outbound",
        "warehouse:bagging", "warehouse:audit",
    ],
    "cashier": [
        "bill:view",
        "finance:cod_handover", "finance:cashier_confirm", "finance:ledger",
    ],
    "accountant": [
        "bill:view", "customer:view",
        "finance:cod_handover", "finance:cashier_confirm", "finance:ledger",
    ],
    "shipper": ["bill:view", "warehouse:outbound"],
}


def upgrade() -> None:
    # 1. Dynamic roles table + seed defaults.
    op.create_table(
        "roles",
        sa.Column("code", sa.Text(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    for code, name in ROLES:
        op.execute(
            sa.text("INSERT INTO roles (code, name) VALUES (:code, :name)").bindparams(
                code=code, name=name
            )
        )

    # 2. Role → action mapping table + seed.
    op.create_table(
        "role_permissions",
        sa.Column("role", sa.Text(), sa.ForeignKey("roles.code", ondelete="CASCADE"), primary_key=True),
        sa.Column("action", sa.Text(), primary_key=True),
    )
    for code, actions in ROLE_PERMISSIONS.items():
        for action in actions:
            op.execute(
                sa.text(
                    "INSERT INTO role_permissions (role, action) VALUES (:role, :action)"
                ).bindparams(role=code, action=action)
            )

    # 3. Point users.role at roles.code: drop the fixed enum check, fix the stale
    #    server_default, and add the FK.
    op.drop_constraint(op.f("ck_users_ck_users_role"), "users", type_="check")
    op.alter_column("users", "role", existing_type=sa.Text(), server_default="operator")
    op.create_foreign_key(
        op.f("fk_users_role_roles"), "users", "roles", ["role"], ["code"]
    )

    # 4. Drop the permission-group indirection.
    op.drop_table("user_permission_groups")
    op.drop_table("permission_actions")
    op.drop_table("permission_groups")


def downgrade() -> None:
    # Recreate the legacy permission-group tables.
    op.create_table(
        "permission_groups",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_table(
        "permission_actions",
        sa.Column(
            "group_id",
            sa.Integer(),
            sa.ForeignKey("permission_groups.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("action", sa.Text(), primary_key=True),
    )
    op.create_table(
        "user_permission_groups",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "group_id",
            sa.Integer(),
            sa.ForeignKey("permission_groups.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # Restore users.role as a fixed enum column.
    op.drop_constraint(op.f("fk_users_role_roles"), "users", type_="foreignkey")
    op.alter_column("users", "role", existing_type=sa.Text(), server_default="staff")
    op.create_check_constraint(
        op.f("ck_users_ck_users_role"),
        "users",
        "role IN ('shipper', 'depot_manager', 'cashier', 'accountant', 'operator', 'admin')",
    )

    op.drop_table("role_permissions")
    op.drop_table("roles")
