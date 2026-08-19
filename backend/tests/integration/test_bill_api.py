"""Integration tests for Bill API (UC-WEB-19 — create bill).

Uses testcontainers[postgres] + asyncpg for real PostgreSQL testing.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import create_access_token
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.service_tier import ServiceTier
from app.models.user import User

from testcontainers.postgres import PostgresContainer

postgres_container = PostgresContainer("postgres:16-alpine", driver="asyncpg")


def get_async_database_url() -> str:
    host = postgres_container.get_container_host_ip()
    port = postgres_container.get_exposed_port(5432)
    return f"postgresql+asyncpg://{postgres_container.username}:{postgres_container.password}@{host}:{port}/{postgres_container.dbname}"


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
        # The tracking-number sequence is created by migrations, not the ORM models.
        await conn.execute(text("CREATE SEQUENCE IF NOT EXISTS bill_tracking_seq START 1 CACHE 50"))
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


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
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
async def auth_headers(admin_user: User) -> dict[str, str]:
    token = create_access_token(admin_user.id, admin_user.username)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def service_tier(db_session: AsyncSession) -> ServiceTier:
    tier = ServiceTier(code="CPN", display_name="Chuyển phát nhanh", scope="domestic", is_active=True)
    db_session.add(tier)
    await db_session.commit()
    return tier


def bill_payload(**overrides) -> dict:
    payload = {
        "sender": {
            "name": "Nguyễn Văn A",
            "phone": "0901234567",
            "address_detail": "12 Lê Lợi",
            "province_code": "79",
            "province_name": "TP. Hồ Chí Minh",
            "ward_code": "26734",
            "ward_name": "Phường Bến Nghé",
        },
        "receiver": {
            "name": "Trần Thị B",
            "phone": "0987654321",
            "address_detail": "45 Nguyễn Huệ",
            "province_code": "79",
            "province_name": "TP. Hồ Chí Minh",
            "ward_code": "26734",
            "ward_name": "Phường Bến Nghé",
        },
        "cargo_type": "goods",
        "service_tier_code": "CPN",
        "actual_weight_kg": 1.0,
        "contents": [
            {
                "description": "Quần áo",
                "quantity": 1,
                "weight_kg": 1.0,
                "length_cm": 20,
                "width_cm": 15,
                "height_cm": 10,
            }
        ],
        "is_insurance_required": False,
        "cod_amount": 1500000,
        "fee": {
            "fee_main": 25000,
            "fee_insurance": 0,
            "fee_other": 0,
            "fee_vat": 2500,
            "fee_total": 27500,
        },
        "payer": "sender",
    }
    payload.update(overrides)
    return payload


@pytest.mark.asyncio
class TestCreateBill:
    async def test_create_bill_success(
        self, client: AsyncClient, auth_headers: dict, service_tier: ServiceTier
    ):
        resp = await client.post("/api/v1/bills", json=bill_payload(), headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["tracking_number"]
        assert data["status"] == "created"
        assert data["sender"]["name"] == "Nguyễn Văn A"
        assert data["receiver"]["name"] == "Trần Thị B"
        assert data["actual_weight_kg"] == 1.0
        # dim = 20*15*10/6000 = 0.5 → chargeable = max(1.0, 0.5) = 1.0
        assert data["chargeable_weight_kg"] == 1.0
        assert data["cod_amount"] == 1500000
        assert data["fee"]["fee_total"] == 27500
        assert len(data["contents"]) == 1

    async def test_chargeable_weight_uses_dim_when_larger(
        self, client: AsyncClient, auth_headers: dict, service_tier: ServiceTier
    ):
        payload = bill_payload(
            actual_weight_kg=0.1,
            contents=[{
                "description": "Hàng cồng kềnh",
                "quantity": 1,
                "weight_kg": 0.1,
                "length_cm": 60,
                "width_cm": 40,
                "height_cm": 30,
            }],
        )
        resp = await client.post("/api/v1/bills", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        # dim = 60*40*30/6000 = 12.0 → chargeable = max(0.1, 12.0) = 12.0
        assert resp.json()["chargeable_weight_kg"] == 12.0

    async def test_create_bill_without_service_tier(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.post("/api/v1/bills", json=bill_payload(), headers=auth_headers)
        assert resp.status_code == 404
        assert resp.json()["error_code"] == "TIER_NOT_FOUND"

    async def test_create_bill_fee_total_mismatch(
        self, client: AsyncClient, auth_headers: dict, service_tier: ServiceTier
    ):
        payload = bill_payload()
        payload["fee"]["fee_total"] = 99999
        resp = await client.post("/api/v1/bills", json=payload, headers=auth_headers)
        assert resp.status_code == 400
        assert resp.json()["error_code"] == "VALIDATION_ERROR"

    async def test_create_bill_empty_contents(
        self, client: AsyncClient, auth_headers: dict, service_tier: ServiceTier
    ):
        payload = bill_payload(contents=[])
        resp = await client.post("/api/v1/bills", json=payload, headers=auth_headers)
        assert resp.status_code == 400
        assert resp.json()["error_code"] == "CONTENT_LINES_REQUIRED"
