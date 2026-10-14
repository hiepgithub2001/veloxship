"""Integration tests for the dynamic role + role_permission API.

Uses testcontainers[postgres] + asyncpg for real PostgreSQL testing.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.permission import Role
from app.models.user import User

# ---------------------------------------------------------------------------
# Test database setup (PostgreSQL via testcontainers)
# ---------------------------------------------------------------------------

from testcontainers.postgres import PostgresContainer

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
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

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


@pytest_asyncio.fixture
async def admin_role(db_session: AsyncSession) -> Role:
    role = Role(code="admin", name="Quản trị viên")
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession, admin_role: Role) -> User:
    user = User(
        username="admin_test",
        full_name="Admin Tester",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(admin_user: User) -> dict[str, str]:
    token = create_access_token(admin_user.id, admin_user.username)
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestRoles:
    @pytest.mark.asyncio
    async def test_create_role(self, client, auth_headers):
        res = await client.post(
            "/api/v1/roles",
            json={"code": "supervisor", "name": "Giám sát"},
            headers=auth_headers,
        )
        assert res.status_code == 201
        body = res.json()
        assert body["code"] == "supervisor"
        assert body["name"] == "Giám sát"
        assert body["actions"] == []

    @pytest.mark.asyncio
    async def test_create_role_duplicate_code(self, client, auth_headers):
        await client.post(
            "/api/v1/roles", json={"code": "supervisor", "name": "Giám sát"}, headers=auth_headers
        )
        res = await client.post(
            "/api/v1/roles", json={"code": "supervisor", "name": "Khác"}, headers=auth_headers
        )
        assert res.status_code == 409
        assert res.json()["error_code"] == "ROLE_CODE_EXISTS"

    @pytest.mark.asyncio
    async def test_list_roles_includes_user_count(self, client, auth_headers):
        await client.post(
            "/api/v1/roles", json={"code": "supervisor", "name": "Giám sát"}, headers=auth_headers
        )
        res = await client.get("/api/v1/roles", headers=auth_headers)
        assert res.status_code == 200
        codes = {r["code"] for r in res.json()}
        assert "admin" in codes
        assert "supervisor" in codes

    @pytest.mark.asyncio
    async def test_update_role_name(self, client, auth_headers):
        res = await client.patch(
            "/api/v1/roles/admin", json={"name": "Quản trị hệ thống"}, headers=auth_headers
        )
        assert res.status_code == 200
        assert res.json()["name"] == "Quản trị hệ thống"

    @pytest.mark.asyncio
    async def test_delete_admin_role_rejected(self, client, auth_headers):
        res = await client.delete("/api/v1/roles/admin", headers=auth_headers)
        assert res.status_code == 409
        assert res.json()["error_code"] == "CANNOT_DELETE_ADMIN_ROLE"

    @pytest.mark.asyncio
    async def test_delete_role_in_use_rejected(self, client, auth_headers):
        # admin_test user already holds role "admin"; try deleting a role in use.
        res = await client.delete("/api/v1/roles/admin", headers=auth_headers)
        assert res.status_code == 409

    @pytest.mark.asyncio
    async def test_set_role_permissions(self, client, auth_headers):
        await client.post(
            "/api/v1/roles", json={"code": "supervisor", "name": "Giám sát"}, headers=auth_headers
        )
        res = await client.put(
            "/api/v1/roles/supervisor/permissions",
            json={"actions": ["bill:view", "warehouse:inbound"]},
            headers=auth_headers,
        )
        assert res.status_code == 200
        assert sorted(res.json()["actions"]) == ["bill:view", "warehouse:inbound"]

    @pytest.mark.asyncio
    async def test_set_role_permissions_invalid_action(self, client, auth_headers):
        res = await client.put(
            "/api/v1/roles/admin/permissions",
            json={"actions": ["invalid:action"]},
            headers=auth_headers,
        )
        assert res.status_code == 400

    @pytest.mark.asyncio
    async def test_roles_require_admin(self, client):
        res = await client.get("/api/v1/roles")
        assert res.status_code in (401, 403)
