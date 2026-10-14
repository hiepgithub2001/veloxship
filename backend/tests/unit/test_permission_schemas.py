"""Unit tests for role & role-permission schema validation."""

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.permission import (
    RoleCreate,
    RolePermissionsUpdate,
    RoleRead,
    RoleUpdate,
)


class TestRoleCreate:
    """Test RoleCreate validation."""

    def test_valid_create(self):
        schema = RoleCreate(code="supervisor", name="Giám sát")
        assert schema.code == "supervisor"
        assert schema.name == "Giám sát"

    def test_code_is_normalized_to_lowercase(self):
        schema = RoleCreate(code="  Supervisor ", name="Giám sát")
        assert schema.code == "supervisor"

    def test_too_short_code_rejected(self):
        with pytest.raises(ValidationError):
            RoleCreate(code="a", name="X")

    def test_code_starting_with_digit_rejected(self):
        with pytest.raises(ValidationError):
            RoleCreate(code="1abc", name="X")

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            RoleCreate(code="supervisor", name="   ")


class TestRoleUpdate:
    """Test RoleUpdate (partial) validation."""

    def test_empty_update_accepted(self):
        schema = RoleUpdate()
        assert schema.name is None

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            RoleUpdate(name="   ")


class TestRolePermissionsUpdate:
    """Test RolePermissionsUpdate validation."""

    def test_valid_actions(self):
        schema = RolePermissionsUpdate(actions=["bill:view", "warehouse:inbound"])
        assert schema.actions == ["bill:view", "warehouse:inbound"]

    def test_invalid_action_rejected(self):
        with pytest.raises(ValidationError):
            RolePermissionsUpdate(actions=["invalid:action"])


class TestRoleRead:
    """Test RoleRead serialization from ORM-like objects."""

    def test_flattens_role_permission_objects_to_strings(self):
        read = RoleRead(
            code="operator",
            name="Nhân viên quầy",
            description=None,
            is_active=True,
            actions=[
                SimpleNamespace(action="bill:view"),
                SimpleNamespace(action="warehouse:outbound"),
            ],
        )
        assert read.actions == ["bill:view", "warehouse:outbound"]

    def test_accepts_plain_strings(self):
        read = RoleRead(
            code="shipper", name="Bưu tá", description="", is_active=True, actions=["bill:view"]
        )
        assert read.actions == ["bill:view"]
