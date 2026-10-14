"""Integration tests for POST /auth/refresh and the token pair issued by login.

Covers the expiry contract the frontend depends on: a refresh token is the only
thing that can mint a new access token, it must be rejected the moment it is
expired, and it must stop working for a deactivated account.

Uses testcontainers[postgres] + asyncpg for real PostgreSQL testing.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ---------------------------------------------------------------------------
# Test database setup (PostgreSQL via testcontainers)
# ---------------------------------------------------------------------------
from testcontainers.postgres import PostgresContainer

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.permission import Role
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
        password_hash=hash_password("secret123"),
        role="operator",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


REFRESH_URL = "/api/v1/auth/refresh"
LOGIN_URL = "/api/v1/auth/login"


def make_expired_refresh_token(user_id: int, username: str) -> str:
    """Mint a refresh token whose `exp` is already in the past."""
    from datetime import UTC, datetime, timedelta

    payload = {
        "sub": str(user_id),
        "username": username,
        "type": "refresh",
        "exp": datetime.now(UTC) - timedelta(seconds=5),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


# ---------------------------------------------------------------------------
# Login issues a usable pair
# ---------------------------------------------------------------------------


class TestLoginIssuesTokenPair:
    @pytest.mark.asyncio
    async def test_login_returns_both_tokens_and_ttl(self, client, operator_user):
        res = await client.post(
            LOGIN_URL, json={"username": "nvquay01", "password": "secret123"}
        )

        assert res.status_code == 200
        body = res.json()
        assert body["access_token"]
        assert body["refresh_token"]
        assert body["token_type"] == "bearer"
        assert body["expires_in"] == settings.ACCESS_TOKEN_TTL_MINUTES * 60

    @pytest.mark.asyncio
    async def test_login_access_token_authorises_me(self, client, operator_user):
        res = await client.post(
            LOGIN_URL, json={"username": "nvquay01", "password": "secret123"}
        )
        token = res.json()["access_token"]

        me = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert me.status_code == 200
        assert me.json()["username"] == "nvquay01"

    @pytest.mark.asyncio
    async def test_login_rejects_wrong_password(self, client, operator_user):
        res = await client.post(
            LOGIN_URL, json={"username": "nvquay01", "password": "wrong"}
        )
        assert res.status_code == 401
        assert res.json()["error_code"] == "INVALID_CREDENTIALS"


# ---------------------------------------------------------------------------
# Refresh happy path
# ---------------------------------------------------------------------------


class TestRefreshSuccess:
    @pytest.mark.asyncio
    async def test_refresh_returns_a_new_usable_pair(self, client, operator_user):
        login = await client.post(
            LOGIN_URL, json={"username": "nvquay01", "password": "secret123"}
        )
        original_refresh = login.json()["refresh_token"]

        res = await client.post(REFRESH_URL, json={"refresh_token": original_refresh})

        assert res.status_code == 200
        body = res.json()
        assert body["access_token"]
        assert body["expires_in"] == settings.ACCESS_TOKEN_TTL_MINUTES * 60

        # The freshly minted access token must actually work.
        me = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"}
        )
        assert me.status_code == 200
        assert me.json()["username"] == "nvquay01"

    @pytest.mark.asyncio
    async def test_refresh_rotates_the_refresh_token(self, client, operator_user):
        login = await client.post(
            LOGIN_URL, json={"username": "nvquay01", "password": "secret123"}
        )
        original_refresh = login.json()["refresh_token"]

        res = await client.post(REFRESH_URL, json={"refresh_token": original_refresh})

        assert res.status_code == 200
        assert res.json()["refresh_token"] != original_refresh

    @pytest.mark.asyncio
    async def test_refresh_token_is_not_accepted_as_an_access_token(
        self, client, operator_user
    ):
        """A refresh token must not authorise a normal authenticated request."""
        res = await client.post(
            LOGIN_URL, json={"username": "nvquay01", "password": "secret123"}
        )
        refresh_token = res.json()["refresh_token"]

        me = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {refresh_token}"}
        )
        assert me.status_code == 401


# ---------------------------------------------------------------------------
# Refresh rejections — the frontend turns each of these into a login redirect
# ---------------------------------------------------------------------------


class TestRefreshRejections:
    @pytest.mark.asyncio
    async def test_rejects_an_access_token(self, client, operator_user):
        """Type confusion: an access token must not be usable to refresh."""
        access_token = create_access_token(operator_user.id, operator_user.username)

        res = await client.post(REFRESH_URL, json={"refresh_token": access_token})

        assert res.status_code == 401
        assert res.json()["error_code"] == "TOKEN_INVALID"

    @pytest.mark.asyncio
    async def test_rejects_an_expired_refresh_token(self, client, operator_user):
        expired = make_expired_refresh_token(operator_user.id, operator_user.username)

        res = await client.post(REFRESH_URL, json={"refresh_token": expired})

        assert res.status_code == 401
        assert res.json()["error_code"] == "TOKEN_INVALID"

    @pytest.mark.asyncio
    async def test_rejects_a_malformed_token(self, client, operator_user):
        res = await client.post(REFRESH_URL, json={"refresh_token": "not-a-jwt"})

        assert res.status_code == 401
        assert res.json()["error_code"] == "TOKEN_INVALID"

    @pytest.mark.asyncio
    async def test_rejects_a_token_signed_with_the_wrong_secret(self, client, operator_user):
        forged = jwt.encode(
            {"sub": str(operator_user.id), "username": operator_user.username,
             "type": "refresh", "exp": 9999999999},
            "wrong-secret",
            algorithm=settings.JWT_ALGORITHM,
        )

        res = await client.post(REFRESH_URL, json={"refresh_token": forged})

        assert res.status_code == 401
        assert res.json()["error_code"] == "TOKEN_INVALID"

    @pytest.mark.asyncio
    async def test_rejects_a_refresh_token_for_an_unknown_user(self, client, operator_user):
        ghost = create_refresh_token(999_999, "ghost")

        res = await client.post(REFRESH_URL, json={"refresh_token": ghost})

        assert res.status_code == 401
        assert res.json()["error_code"] == "TOKEN_INVALID"

    @pytest.mark.asyncio
    async def test_rejects_a_refresh_token_once_the_account_is_deactivated(
        self, client, operator_user, db_session
    ):
        login = await client.post(
            LOGIN_URL, json={"username": "nvquay01", "password": "secret123"}
        )
        refresh_token = login.json()["refresh_token"]

        operator_user.is_active = False
        db_session.add(operator_user)
        await db_session.commit()

        res = await client.post(REFRESH_URL, json={"refresh_token": refresh_token})

        assert res.status_code == 401
        assert res.json()["error_code"] == "TOKEN_INVALID"

    @pytest.mark.asyncio
    async def test_requires_a_refresh_token_field(self, client, operator_user):
        """A missing field is a request-validation error (400 per handler)."""
        res = await client.post(REFRESH_URL, json={})
        assert res.status_code == 400
        assert res.json()["error_code"] == "VALIDATION_ERROR"
