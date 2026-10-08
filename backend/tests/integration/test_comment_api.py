"""Integration tests for Comment API endpoints.

Uses testcontainers[postgres] + asyncpg for real PostgreSQL testing.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import create_access_token
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.depot import Depot
from app.models.user import User


@pytest_asyncio.fixture(autouse=True)
async def _seed_roles(engine):
    """Seed default roles so the users.role FK is satisfied in integration tests."""
    from app.models.permission import Role

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        for code, name in [
            ("admin", "Quản trị viên"),
            ("operator", "Nhân viên quầy"),
            ("shipper", "Bưu tá"),
            ("depot_manager", "Thủ kho"),
            ("cashier", "Thủ quỹ"),
            ("accountant", "Kế toán"),
        ]:
            session.add(Role(code=code, name=name))
        await session.commit()
    yield

# ---------------------------------------------------------------------------
# Test database setup (PostgreSQL via testcontainers)
# ---------------------------------------------------------------------------

from testcontainers.postgres import PostgresContainer

postgres_container = PostgresContainer("postgres:16-alpine", driver="asyncpg")


def get_async_database_url() -> str:
    """Build asyncpg connection URL from running container."""
    host = postgres_container.get_container_host_ip()
    port = postgres_container.get_exposed_port(5432)
    user = postgres_container.username
    password = postgres_container.password
    dbname = postgres_container.dbname
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"


@pytest.fixture(scope="session", autouse=True)
def start_postgres():
    """Start the PostgreSQL container once for all tests."""
    postgres_container.start()
    yield
    postgres_container.stop()


@pytest_asyncio.fixture
async def engine(start_postgres):
    """Create async engine connected to test PostgreSQL."""
    url = get_async_database_url()
    eng = create_async_engine(url, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def client(engine):
    """Async HTTP client with overridden DB dependency."""
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
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user and return it."""
    user = User(
        username="admin_test",
        full_name="Admin Tester",
        password_hash="hashed",
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def staff_user(db_session: AsyncSession) -> User:
    """Create a non-admin staff user and return it."""
    user = User(
        username="staff_test",
        full_name="Staff Tester",
        password_hash="hashed",
        role="operator",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def db_session(engine):
    """Provide a test database session."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def auth_headers(admin_user: User) -> dict[str, str]:
    """Generate JWT auth headers for the admin user."""
    token = create_access_token(admin_user.id, admin_user.username)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def staff_headers(staff_user: User) -> dict[str, str]:
    """Generate JWT auth headers for the staff user."""
    token = create_access_token(staff_user.id, staff_user.username)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def depot(db_session: AsyncSession) -> Depot:
    """Create a test depot to attach comments to."""
    d = Depot(
        code="BC-CM",
        name="Bưu cục Comment",
        phone="0901234567",
        address_detail="123 Đường Test",
    )
    db_session.add(d)
    await db_session.commit()
    await db_session.refresh(d)
    return d


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def comment_payload(entity_id: int, body: str = "Bình luận test", **overrides) -> dict:
    """Build a comment creation payload."""
    payload: dict = {
        "entity_type": "depot",
        "entity_id": entity_id,
        "body": body,
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestCommentCRUD:
    """Test comment create / list / update / delete lifecycle."""

    async def test_create_root_comment(self, client: AsyncClient, auth_headers: dict, depot: Depot):
        """Create a root comment and verify response fields."""
        resp = await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id, body="Gói hàng cần kiểm tra"),
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["body"] == "Gói hàng cần kiểm tra"
        assert data["entity_type"] == "depot"
        assert data["entity_id"] == depot.id
        assert data["parent_id"] is None
        assert data["author_name"] == "Admin Tester"
        assert data["replies"] == []

    async def test_list_comments_threaded(
        self, client: AsyncClient, auth_headers: dict, depot: Depot
    ):
        """List returns root comments with replies nested inline."""
        root = await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id, body="Root"),
            headers=auth_headers,
        )
        root_id = root.json()["id"]
        await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id, body="Reply", parent_id=root_id),
            headers=auth_headers,
        )

        resp = await client.get(
            "/api/v1/comments",
            params={"entity_type": "depot", "entity_id": depot.id},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["body"] == "Root"
        assert len(data[0]["replies"]) == 1
        assert data[0]["replies"][0]["body"] == "Reply"
        assert data[0]["replies"][0]["parent_id"] == root_id

    async def test_update_comment_by_author(
        self, client: AsyncClient, auth_headers: dict, depot: Depot
    ):
        """Author can update their own comment."""
        created = await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id, body="Trước"),
            headers=auth_headers,
        )
        comment_id = created.json()["id"]

        resp = await client.patch(
            f"/api/v1/comments/{comment_id}",
            json={"body": "Sau khi sửa"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["body"] == "Sau khi sửa"

    async def test_delete_comment_soft(
        self, client: AsyncClient, auth_headers: dict, depot: Depot
    ):
        """Delete soft-removes the comment from the list."""
        created = await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id),
            headers=auth_headers,
        )
        comment_id = created.json()["id"]

        resp = await client.delete(f"/api/v1/comments/{comment_id}", headers=auth_headers)
        assert resp.status_code == 204

        listed = await client.get(
            "/api/v1/comments",
            params={"entity_type": "depot", "entity_id": depot.id},
            headers=auth_headers,
        )
        assert listed.json() == []

    async def test_delete_cascades_replies(
        self, client: AsyncClient, auth_headers: dict, depot: Depot
    ):
        """Deleting a root comment soft-deletes its replies too."""
        root = await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id, body="Root"),
            headers=auth_headers,
        )
        root_id = root.json()["id"]
        await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id, body="Reply", parent_id=root_id),
            headers=auth_headers,
        )

        await client.delete(f"/api/v1/comments/{root_id}", headers=auth_headers)

        listed = await client.get(
            "/api/v1/comments",
            params={"entity_type": "depot", "entity_id": depot.id},
            headers=auth_headers,
        )
        assert listed.json() == []


@pytest.mark.asyncio
class TestCommentValidation:
    """Test validation and error responses."""

    async def test_entity_not_found(self, client: AsyncClient, auth_headers: dict):
        """Creating a comment on a missing entity returns 404."""
        resp = await client.post(
            "/api/v1/comments",
            json=comment_payload(99999),
            headers=auth_headers,
        )
        assert resp.status_code == 404
        assert resp.json()["error_code"] == "COMMENT_ENTITY_NOT_FOUND"

    async def test_invalid_entity_type_on_list(self, client: AsyncClient, auth_headers: dict):
        """Listing with an unknown entity_type returns 422."""
        resp = await client.get(
            "/api/v1/comments",
            params={"entity_type": "nope", "entity_id": 1},
            headers=auth_headers,
        )
        assert resp.status_code == 422
        assert resp.json()["error_code"] == "COMMENT_ENTITY_INVALID"

    async def test_reply_parent_missing(self, client: AsyncClient, auth_headers: dict, depot: Depot):
        """Replying to a non-existent parent returns 404."""
        resp = await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id, body="Reply", parent_id=99999),
            headers=auth_headers,
        )
        assert resp.status_code == 404
        assert resp.json()["error_code"] == "COMMENT_PARENT_INVALID"

    async def test_reply_to_reply_rejected(
        self, client: AsyncClient, auth_headers: dict, depot: Depot
    ):
        """Replying to a reply (depth > 1) returns 409."""
        root = await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id, body="Root"),
            headers=auth_headers,
        )
        root_id = root.json()["id"]
        reply = await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id, body="Reply", parent_id=root_id),
            headers=auth_headers,
        )
        reply_id = reply.json()["id"]

        resp = await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id, body="Reply of reply", parent_id=reply_id),
            headers=auth_headers,
        )
        assert resp.status_code == 409
        assert resp.json()["error_code"] == "COMMENT_PARENT_INVALID"

    async def test_comment_not_found(self, client: AsyncClient, auth_headers: dict):
        """Updating a missing comment returns 404."""
        resp = await client.patch(
            "/api/v1/comments/99999",
            json={"body": "x"},
            headers=auth_headers,
        )
        assert resp.status_code == 404
        assert resp.json()["error_code"] == "COMMENT_NOT_FOUND"

    async def test_body_required(self, client: AsyncClient, auth_headers: dict, depot: Depot):
        """Empty body is rejected with 400 validation error."""
        resp = await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id, body="   "),
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert resp.json()["error_code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
class TestCommentPermissions:
    """Test ownership / permission rules."""

    async def test_non_author_cannot_update(
        self, client: AsyncClient, auth_headers: dict, staff_headers: dict, depot: Depot
    ):
        """A staff user cannot edit someone else's comment."""
        created = await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id),
            headers=auth_headers,
        )
        comment_id = created.json()["id"]

        resp = await client.patch(
            f"/api/v1/comments/{comment_id}",
            json={"body": "Hack"},
            headers=staff_headers,
        )
        assert resp.status_code == 403
        assert resp.json()["error_code"] == "COMMENT_FORBIDDEN"

    async def test_non_author_cannot_delete(
        self, client: AsyncClient, auth_headers: dict, staff_headers: dict, depot: Depot
    ):
        """A staff user cannot delete someone else's comment."""
        created = await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id),
            headers=auth_headers,
        )
        comment_id = created.json()["id"]

        resp = await client.delete(f"/api/v1/comments/{comment_id}", headers=staff_headers)
        assert resp.status_code == 403

    async def test_admin_can_delete_others_comment(
        self, client: AsyncClient, auth_headers: dict, staff_headers: dict, depot: Depot
    ):
        """Admin can delete a comment authored by another user."""
        created = await client.post(
            "/api/v1/comments",
            json=comment_payload(depot.id),
            headers=staff_headers,
        )
        comment_id = created.json()["id"]

        resp = await client.delete(f"/api/v1/comments/{comment_id}", headers=auth_headers)
        assert resp.status_code == 204

    async def test_unauthenticated_request(self, client: AsyncClient):
        """Request without auth returns 401/403."""
        resp = await client.get(
            "/api/v1/comments",
            params={"entity_type": "depot", "entity_id": 1},
        )
        assert resp.status_code in (401, 403)
