"""Unit tests for the authorization helpers and the status→action map.

Covers `app.api.v1.deps.authorize` with a stubbed session so the permission
matrix (admin bypass, granted, missing, inactive/unknown role) is pinned down
without a database.
"""

from types import SimpleNamespace

import pytest

from app.api.v1 import deps
from app.core.exceptions import ForbiddenError
from app.core.permissions import STATUS_ACTION_MAP, is_valid_action, status_action
from app.crud import permission as permission_crud

# ---------------------------------------------------------------------------
# STATUS_ACTION_MAP
# ---------------------------------------------------------------------------


class TestStatusActionMap:
    def test_every_mapped_action_is_in_the_catalogue(self):
        for action in STATUS_ACTION_MAP.values():
            assert is_valid_action(action), f"{action} is not a catalogue action"

    def test_covers_every_bill_status_that_can_be_entered(self):
        # `created` is the initial status, never a transition target.
        for status in ("picked_up", "in_transit", "delivered", "returned", "cancelled"):
            assert status in STATUS_ACTION_MAP
            assert status_action(status) is not None

    def test_unknown_status_has_no_action(self):
        assert status_action("teleported") is None
        assert status_action("created") is None


# ---------------------------------------------------------------------------
# authorize()
# ---------------------------------------------------------------------------


class _StubDb:
    """Minimal async session stub — only `get(Role, code)` is exercised."""

    def __init__(self, role):
        self._role = role

    async def get(self, _model, _pk):
        return self._role


def _role(code: str = "operator", is_active: bool = True):
    return SimpleNamespace(code=code, is_active=is_active)


def _user(role: str = "operator"):
    return SimpleNamespace(role=role)


def _grant(monkeypatch, granted: set[str]) -> None:
    async def _get_role_permission_actions(_db, _role):
        return granted

    monkeypatch.setattr(
        permission_crud, "get_role_permission_actions", _get_role_permission_actions
    )


@pytest.mark.asyncio
async def test_admin_bypasses_every_check():
    # No db access at all for the reserved admin role.
    await deps.authorize(_StubDb(None), _user("admin"), "bill:create")


@pytest.mark.asyncio
async def test_granted_action_is_allowed(monkeypatch):
    _grant(monkeypatch, {"bill:create", "bill:view"})
    await deps.authorize(_StubDb(_role()), _user(), "bill:create")


@pytest.mark.asyncio
async def test_any_of_several_actions_is_allowed(monkeypatch):
    _grant(monkeypatch, {"warehouse:outbound"})
    await deps.authorize(_StubDb(_role()), _user(), "bill:cancel", "warehouse:outbound")


@pytest.mark.asyncio
async def test_missing_action_is_forbidden(monkeypatch):
    _grant(monkeypatch, {"bill:view"})
    with pytest.raises(ForbiddenError):
        await deps.authorize(_StubDb(_role()), _user(), "bill:create")


@pytest.mark.asyncio
async def test_inactive_role_grants_nothing(monkeypatch):
    _grant(monkeypatch, {"bill:create"})
    with pytest.raises(ForbiddenError):
        await deps.authorize(_StubDb(_role(is_active=False)), _user(), "bill:create")


@pytest.mark.asyncio
async def test_unknown_role_grants_nothing(monkeypatch):
    _grant(monkeypatch, {"bill:create"})
    with pytest.raises(ForbiddenError):
        await deps.authorize(_StubDb(None), _user("ghost"), "bill:create")


@pytest.mark.asyncio
async def test_empty_action_list_fails_closed(monkeypatch):
    _grant(monkeypatch, {"bill:create"})
    with pytest.raises(ForbiddenError):
        await deps.authorize(_StubDb(_role()), _user())
