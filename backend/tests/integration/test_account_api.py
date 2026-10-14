"""Integration tests for self-service account endpoints (PATCH /auth/me, change-password).

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
async def operator_role(db_session: AsyncSession) -> Role:
    """Create the operator role (users.role is a FK to roles.code)."""
    role = Role(code="operator", name="Nhân viên quầy")
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest_asyncio.fixture
async def operator_user(db_session: AsyncSession, operator_role: Role) -> User:
    """Create an active operator user with a known password."""
    user = User(
        username="nvquay01",
        full_name="Nguyễn Văn A",
        phone="0901234567",
        password_hash=hash_password("oldpass123"),
        role="operator",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(operator_user: User) -> dict[str, str]:
    token = create_access_token(operator_user.id, operator_user.username)
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGetMe:
    @pytest.mark.asyncio
    async def test_me_includes_avatar_field(self, client, auth_headers):
        res = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert body["username"] == "nvquay01"
        assert "avatar" in body


class TestUpdateMe:
    @pytest.mark.asyncio
    async def test_update_full_name_and_phone(self, client, auth_headers):
        res = await client.patch(
            "/api/v1/auth/me",
            json={"full_name": "Nguyễn Văn B", "phone": "0909999999"},
            headers=auth_headers,
        )
        assert res.status_code == 200
        body = res.json()
        assert body["full_name"] == "Nguyễn Văn B"
        assert body["phone"] == "0909999999"

    @pytest.mark.asyncio
    async def test_update_rejects_duplicate_phone(self, client, auth_headers, db_session):
        other = User(
            username="other01",
            full_name="Người Khác",
            phone="0908888888",
            password_hash=hash_password("whatever123"),
            role="operator",
            is_active=True,
        )
        db_session.add(other)
        await db_session.commit()

        res = await client.patch(
            "/api/v1/auth/me", json={"phone": "0908888888"}, headers=auth_headers
        )
        assert res.status_code == 409
        assert res.json()["error_code"] == "PHONE_EXISTS"

    @pytest.mark.asyncio
    async def test_update_rejects_invalid_phone(self, client, auth_headers):
        res = await client.patch(
            "/api/v1/auth/me", json={"phone": "123"}, headers=auth_headers
        )
        assert res.status_code == 400

    @pytest.mark.asyncio
    async def test_unauthenticated_rejected(self, client):
        res = await client.patch("/api/v1/auth/me", json={"full_name": "X"})
        assert res.status_code in (401, 403)


class TestChangePassword:
    @pytest.mark.asyncio
    async def test_change_password_success(self, client, auth_headers):
        res = await client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "oldpass123", "new_password": "newpass123"},
            headers=auth_headers,
        )
        assert res.status_code == 200
        assert res.json()["message"]

    @pytest.mark.asyncio
    async def test_change_password_rejects_wrong_current(self, client, auth_headers):
        res = await client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "wrongpass", "new_password": "newpass123"},
            headers=auth_headers,
        )
        assert res.status_code == 400
        assert res.json()["error_code"] == "CURRENT_PASSWORD_INCORRECT"

    @pytest.mark.asyncio
    async def test_change_password_rejects_same_as_current(self, client, auth_headers):
        res = await client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "oldpass123", "new_password": "oldpass123"},
            headers=auth_headers,
        )
        assert res.status_code == 400
        assert res.json()["error_code"] == "NEW_PASSWORD_SAME_AS_CURRENT"

    @pytest.mark.asyncio
    async def test_change_password_rejects_short_new(self, client, auth_headers):
        res = await client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "oldpass123", "new_password": "123"},
            headers=auth_headers,
        )
        assert res.status_code == 400
