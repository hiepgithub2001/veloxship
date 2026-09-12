"""Integration tests for Bill API (UC-WEB-19 — create bill).

Uses testcontainers[postgres] + asyncpg for real PostgreSQL testing.
"""

from datetime import UTC, datetime, timedelta

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
from app.models.service_tier import ServiceTier
from app.models.user import User

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
    tier = ServiceTier(
        code="CPN", display_name="Chuyển phát nhanh", scope="domestic", is_active=True
    )
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
            contents=[
                {
                    "description": "Hàng cồng kềnh",
                    "quantity": 1,
                    "weight_kg": 0.1,
                    "length_cm": 60,
                    "width_cm": 40,
                    "height_cm": 30,
                }
            ],
        )
        resp = await client.post("/api/v1/bills", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        # dim = 60*40*30/6000 = 12.0 → chargeable = max(0.1, 12.0) = 12.0
        assert resp.json()["chargeable_weight_kg"] == 12.0

    async def test_create_bill_without_service_tier(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/api/v1/bills", json=bill_payload(), headers=auth_headers)
        assert resp.status_code == 404
        assert resp.json()["error_code"] == "TIER_NOT_FOUND"

    async def test_create_bill_omits_optional_fields_with_images(
        self, client: AsyncClient, auth_headers: dict
    ):
        payload = bill_payload()
        for key in (
            "cargo_type",
            "service_tier_code",
            "actual_weight_kg",
            "is_insurance_required",
            "cod_amount",
        ):
            payload.pop(key, None)
        payload["contents"][0]["images"] = ["images/sample-1.jpg"]

        resp = await client.post("/api/v1/bills", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["cargo_type"] == "goods"
        assert data["service_tier_code"] is None
        assert data["actual_weight_kg"] == 0
        assert data["is_insurance_required"] is False
        assert data["cod_amount"] == 0
        assert len(data["contents"][0]["images"]) == 1
        assert data["contents"][0]["images"][0].startswith("http")

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


@pytest.mark.asyncio
class TestListBills:
    async def test_searches_by_tracking_number_customer_name_phone_and_bill_id(
        self, client: AsyncClient, auth_headers: dict, service_tier: ServiceTier
    ):
        created = await client.post(
            "/api/v1/bills",
            json=bill_payload(),
            headers=auth_headers,
        )
        assert created.status_code == 201
        bill = created.json()

        for search in (
            bill["tracking_number"],
            "nguyen van",
            "0901234567",
            "0987654321",
            str(bill["id"]),
        ):
            response = await client.get(
                "/api/v1/bills",
                params={"search": search},
                headers=auth_headers,
            )
            assert response.status_code == 200
            assert [item["id"] for item in response.json()["items"]] == [bill["id"]]

        literal_wildcard_search = await client.get(
            "/api/v1/bills",
            params={"search": "%"},
            headers=auth_headers,
        )
        assert literal_wildcard_search.status_code == 200
        assert literal_wildcard_search.json()["items"] == []

        for non_representable_id in ("²", "9" * 100):
            response = await client.get(
                "/api/v1/bills",
                params={"search": non_representable_id},
                headers=auth_headers,
            )
            assert response.status_code == 200

    async def test_filters_by_status(
        self, client: AsyncClient, auth_headers: dict, service_tier: ServiceTier
    ):
        b1 = await client.post("/api/v1/bills", json=bill_payload(), headers=auth_headers)
        b2 = await client.post("/api/v1/bills", json=bill_payload(), headers=auth_headers)
        id1, id2 = b1.json()["id"], b2.json()["id"]

        moved = await client.post(
            f"/api/v1/bills/{id2}/status",
            json={"to_status": "picked_up"},
            headers=auth_headers,
        )
        assert moved.status_code == 200

        picked = await client.get(
            "/api/v1/bills", params={"status": "picked_up"}, headers=auth_headers
        )
        assert [item["id"] for item in picked.json()["items"]] == [id2]

        created = await client.get(
            "/api/v1/bills", params={"status": "created"}, headers=auth_headers
        )
        assert [item["id"] for item in created.json()["items"]] == [id1]

    async def test_filters_by_created_date_range(
        self, client: AsyncClient, auth_headers: dict, service_tier: ServiceTier
    ):
        created = await client.post("/api/v1/bills", json=bill_payload(), headers=auth_headers)
        bill_id = created.json()["id"]

        now = datetime.now(UTC)
        window = await client.get(
            "/api/v1/bills",
            params={
                "created_from": (now - timedelta(hours=1)).isoformat(),
                "created_to": (now + timedelta(hours=1)).isoformat(),
            },
            headers=auth_headers,
        )
        assert bill_id in [item["id"] for item in window.json()["items"]]

        past = await client.get(
            "/api/v1/bills",
            params={
                "created_from": (now - timedelta(days=365)).isoformat(),
                "created_to": (now - timedelta(days=364)).isoformat(),
            },
            headers=auth_headers,
        )
        assert bill_id not in [item["id"] for item in past.json()["items"]]

    async def test_unknown_status_returns_400(
        self, client: AsyncClient, auth_headers: dict, service_tier: ServiceTier
    ):
        resp = await client.get(
            "/api/v1/bills", params={"status": "bogus"}, headers=auth_headers
        )
        assert resp.status_code == 400
        assert resp.json()["error_code"] == "VALIDATION_ERROR"
