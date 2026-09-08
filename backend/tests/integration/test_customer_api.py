"""Integration tests for the read-only customer directory."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.security import create_access_token
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.customer import Customer
from app.models.user import User

postgres_container = PostgresContainer("postgres:16-alpine", driver="asyncpg")


@pytest.fixture(scope="session", autouse=True)
def start_postgres():
    postgres_container.start()
    yield
    postgres_container.stop()


@pytest_asyncio.fixture
async def engine(start_postgres):
    url = (
        f"postgresql+asyncpg://{postgres_container.username}:{postgres_container.password}"
        f"@{postgres_container.get_container_host_ip()}:{postgres_container.get_exposed_port(5432)}"
        f"/{postgres_container.dbname}"
    )
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent"))
        await conn.execute(
            text("""
            CREATE OR REPLACE FUNCTION f_unaccent(text)
            RETURNS text AS $$
            SELECT public.unaccent('public.unaccent', $1)
            $$ LANGUAGE sql IMMUTABLE STRICT;
        """)
        )
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(engine):
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http_client:
        yield http_client
    app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture
async def auth_headers(engine) -> dict[str, str]:
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        user = User(
            username="customer_admin",
            full_name="Customer Admin",
            password_hash="hashed",
            role="admin",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return {"Authorization": f"Bearer {create_access_token(user.id, user.username)}"}


@pytest_asyncio.fixture
async def customers(engine):
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add_all(
            [
                Customer(
                    code="KH-001",
                    name="Cửa hàng Hà Nội",
                    phone="0901000001",
                    customer_type="shop",
                    customer_metadata={"address_detail": "1 Phố Huế", "province_name": "Hà Nội"},
                ),
                Customer(name="Nguyễn Văn Bình", phone="0901000002", is_active=False),
            ]
        )
        await session.commit()


@pytest.mark.asyncio
async def test_customer_directory_searches_without_accents_and_filters_status(
    client: AsyncClient,
    auth_headers: dict[str, str],
    customers,
):
    response = await client.get(
        "/api/v1/customers",
        params={"search": "cua hang ha noi", "is_active": "true"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "Cửa hàng Hà Nội"
    assert body["items"][0]["metadata"]["province_name"] == "Hà Nội"


@pytest.mark.asyncio
async def test_customer_directory_detail_and_manual_creation_is_not_exposed(
    client: AsyncClient,
    auth_headers: dict[str, str],
    customers,
):
    listing = await client.get("/api/v1/customers", headers=auth_headers)
    customer_id = listing.json()["items"][0]["id"]

    detail = await client.get(f"/api/v1/customers/{customer_id}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["id"] == customer_id

    create = await client.post("/api/v1/customers", json={"name": "Manual"}, headers=auth_headers)
    assert create.status_code == 405
