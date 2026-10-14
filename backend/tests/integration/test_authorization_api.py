"""Integration tests for the fine-grained authorization middleware.

Proves that endpoints are gated by permission ACTION (not by a hardcoded role
list): a role granted an action may call it, a role without it gets 403, the
reserved `admin` role bypasses every check, and a NON-admin role holding
`iam:manage_permissions` can reach the role-management API.

Uses testcontainers[postgres] + asyncpg for real PostgreSQL testing.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.permission import Role, RolePermission
from app.models.user import User

postgres_container = PostgresContainer("postgres:16-alpine", driver="asyncpg")


def get_async_database_url() -> str:
    host = postgres_container.get_container_host_ip()
    port = postgres_container.get_exposed_port(5432)
    user = postgres_container.username
    password = postgres_container.password
    dbname = postgres_container.dbname
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"


@pytest.fixture(scope="session", autouse=True)
def start_postgres():
    postgres_container.start()
    yield
    postgres_container.stop()


@pytest_asyncio.fixture
async def engine(start_postgres):
    url = get_async_database_url()
    eng = create_async_engine(url, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(engine):
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


async def _add_role(
    db_session: AsyncSession, code: str, name: str, actions: set[str]
) -> Role:
    role = Role(code=code, name=name)
    role.permissions = [
        RolePermission(role=code, action=action) for action in sorted(actions)
    ]
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


async def _add_user(db_session: AsyncSession, username: str, role: str) -> User:
    user = User(
        username=username,
        full_name=username.title(),
        password_hash=hash_password("secret123"),
        role=role,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


def _headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id, user.username)}"}


@pytest_asyncio.fixture
async def admin_headers(db_session: AsyncSession) -> dict[str, str]:
    await _add_role(db_session, "admin", "Quản trị viên", set())
    user = await _add_user(db_session, "admin_auth", "admin")
    return _headers(user)


@pytest_asyncio.fixture
async def clerk_headers(db_session: AsyncSession) -> dict[str, str]:
    """Role with viewing rights only — no manage rights at all."""
    await _add_role(
        db_session,
        "clerk",
        "Nhân viên quầy",
        {"bill:view", "customer:view", "depot:view", "fleet:view"},
    )
    user = await _add_user(db_session, "clerk_auth", "clerk")
    return _headers(user)


@pytest_asyncio.fixture
async def iam_headers(db_session: AsyncSession) -> dict[str, str]:
    """A NON-admin role granted role-management: proves the gate is dynamic."""
    await _add_role(
        db_session, "roleadmin", "Quản trị vai trò", {"iam:manage_permissions"}
    )
    user = await _add_user(db_session, "roleadmin_auth", "roleadmin")
    return _headers(user)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestPermissionGating:
    @pytest.mark.asyncio
    async def test_granted_action_is_allowed(self, client, clerk_headers):
        for path in (
            "/api/v1/bills",
            "/api/v1/customers",
            "/api/v1/depots",
            "/api/v1/vehicles",
        ):
            res = await client.get(path, headers=clerk_headers)
            assert res.status_code == 200, f"{path} → {res.status_code}"

    @pytest.mark.asyncio
    async def test_missing_action_is_forbidden(self, client, clerk_headers):
        # `clerk` holds no iam:* and no depot:manage action.
        for path in ("/api/v1/users", "/api/v1/roles", "/api/v1/permissions/catalog"):
            res = await client.get(path, headers=clerk_headers)
            assert res.status_code == 403, f"{path} → {res.status_code}"
            assert res.json()["error_code"] == "FORBIDDEN"

    @pytest.mark.asyncio
    async def test_write_endpoint_requires_manage_action(self, client, clerk_headers):
        res = await client.post(
            "/api/v1/depots",
            json={"code": "BC99", "name": "Bưu cục 99"},
            headers=clerk_headers,
        )
        assert res.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_bypasses_every_check(self, client, admin_headers):
        for path in ("/api/v1/users", "/api/v1/roles", "/api/v1/permissions/catalog"):
            res = await client.get(path, headers=admin_headers)
            assert res.status_code == 200, f"{path} → {res.status_code}"

    @pytest.mark.asyncio
    async def test_non_admin_role_with_grant_can_manage_roles(
        self, client, iam_headers
    ):
        res = await client.get("/api/v1/roles", headers=iam_headers)
        assert res.status_code == 200
        assert any(role["code"] == "roleadmin" for role in res.json())

    @pytest.mark.asyncio
    async def test_unauthenticated_request_is_rejected(self, client):
        res = await client.get("/api/v1/depots")
        assert res.status_code in (401, 403)
