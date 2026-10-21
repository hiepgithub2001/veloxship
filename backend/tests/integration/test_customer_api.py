"""Integration tests for the customer module.

Covers the directory (search/filter), manual create, partial update, the
permission gates, bill history, and activity metrics.

Uses testcontainers[postgres] + asyncpg for real PostgreSQL testing.
"""

from datetime import datetime
from decimal import Decimal

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
from app.models.bill import Bill
from app.models.customer import Customer
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
        # Customer codes come from a DB sequence created by the migration, which
        # `create_all` does not model — create it here so manual create works.
        await conn.execute(
            text("CREATE SEQUENCE IF NOT EXISTS customer_code_seq START 1 CACHE 50")
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
async def viewer_headers(engine) -> dict[str, str]:
    """A non-admin role holding ONLY `customer:view` (so create/update must 403)."""
    from app.models.permission import Role, RolePermission

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(Role(code="viewer", name="Chỉ xem"))
        await session.flush()
        session.add(RolePermission(role="viewer", action="customer:view"))
        user = User(
            username="customer_viewer",
            full_name="Customer Viewer",
            password_hash="hashed",
            role="viewer",
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


@pytest_asyncio.fixture
async def activity(engine):
    """Customer A plus three bills: delivered cost, receiver-only, cancelled."""
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        sender = Customer(name="Người gửi A", phone="0902000001", customer_type="retail")
        other = Customer(name="Người nhận B", phone="0902000002", customer_type="retail")
        user = User(
            username="bill_creator",
            full_name="Bill Creator",
            password_hash="hashed",
            role="admin",
        )
        session.add_all([sender, other, user])
        await session.flush()

        common = {
            "cargo_type": "goods",
            "payer": "sender",
            "actual_weight_kg": Decimal("1.000"),
            "chargeable_weight_kg": Decimal("1.000"),
            "created_by": user.id,
            "updated_by": user.id,
        }
        session.add_all(
            [
                # A sends, 100.000, delivered -> counts toward A's revenue
                Bill(
                    tracking_number="VD0001",
                    sender_id=sender.id,
                    receiver_id=other.id,
                    fee_main=Decimal("100000.00"),
                    fee_total=Decimal("100000.00"),
                    status="delivered",
                    delivered_at=datetime.now(),
                    delivered_to_name="Người nhận B",
                    **common,
                ),
                # A receives only, 200.000 -> counted in total_bills, NOT revenue
                Bill(
                    tracking_number="VD0002",
                    sender_id=other.id,
                    receiver_id=sender.id,
                    fee_main=Decimal("200000.00"),
                    fee_total=Decimal("200000.00"),
                    status="created",
                    **common,
                ),
                # A sends, 300.000, cancelled -> counted, excluded from revenue
                Bill(
                    tracking_number="VD0003",
                    sender_id=sender.id,
                    receiver_id=other.id,
                    fee_main=Decimal("300000.00"),
                    fee_total=Decimal("300000.00"),
                    status="cancelled",
                    cancellation_reason="Khách huỷ",
                    **common,
                ),
            ]
        )
        await session.commit()
        await session.refresh(sender)
        return {"sender_id": sender.id, "other_id": other.id}


async def _customer_id_by_code(
    client: AsyncClient, headers: dict[str, str], code: str = "KH-001"
) -> int:
    """Resolve the seeded customer that carries address metadata."""
    listing = await client.get("/api/v1/customers", params={"search": code}, headers=headers)
    return listing.json()["items"][0]["id"]


# ---------------------------------------------------------------------------
# Directory
# ---------------------------------------------------------------------------


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
    # Address is also flattened out of metadata for the edit form.
    assert body["items"][0]["province_name"] == "Hà Nội"
    assert body["items"][0]["address_detail"] == "1 Phố Huế"


@pytest.mark.asyncio
async def test_customer_detail_returns_profile(
    client: AsyncClient,
    auth_headers: dict[str, str],
    customers,
):
    listing = await client.get("/api/v1/customers", headers=auth_headers)
    customer_id = listing.json()["items"][0]["id"]

    detail = await client.get(f"/api/v1/customers/{customer_id}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["id"] == customer_id


@pytest.mark.asyncio
async def test_customer_detail_not_found(client, auth_headers):
    response = await client.get("/api/v1/customers/999999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error_code"] == "CUSTOMER_NOT_FOUND"


# ---------------------------------------------------------------------------
# Manual create
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_customer_generates_code_and_stores_address(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    response = await client.post(
        "/api/v1/customers",
        json={
            "name": "Công ty Vận tải Sài Gòn",
            "phone": "0908000001",
            "customer_type": "enterprise",
            "address_detail": "12 Nguyễn Huệ",
            "province_code": "79",
            "province_name": "TP. Hồ Chí Minh",
            "ward_name": "Bến Nghé",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["code"].startswith("KH")
    assert body["customer_type"] == "enterprise"
    assert body["is_active"] is True
    assert body["metadata"]["address_detail"] == "12 Nguyễn Huệ"
    assert body["province_name"] == "TP. Hồ Chí Minh"
    assert body["ward_name"] == "Bến Nghé"


@pytest.mark.asyncio
async def test_create_customer_allows_duplicate_phone(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    """Duplicate phones must never block: bill entry resolves customers by phone."""
    payload = {"name": "Khách trùng SĐT", "phone": "0908000009"}

    first = await client.post("/api/v1/customers", json=payload, headers=auth_headers)
    second = await client.post("/api/v1/customers", json=payload, headers=auth_headers)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["code"] != second.json()["code"]


@pytest.mark.asyncio
async def test_create_customer_rejects_unknown_type(client, auth_headers):
    response = await client.post(
        "/api/v1/customers",
        json={"name": "Khách VIP", "customer_type": "vip"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_create_customer_rejects_empty_name(client, auth_headers):
    response = await client.post(
        "/api/v1/customers",
        json={"name": ""},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# Partial update
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_customer_merges_metadata_and_keeps_code(
    client: AsyncClient,
    auth_headers: dict[str, str],
    customers,
):
    customer_id = await _customer_id_by_code(client, auth_headers)
    original_code = (
        await client.get(f"/api/v1/customers/{customer_id}", headers=auth_headers)
    ).json()["code"]

    response = await client.patch(
        f"/api/v1/customers/{customer_id}",
        json={"name": "Cửa hàng Hà Nội (mới)", "ward_name": "Phúc Tân"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Cửa hàng Hà Nội (mới)"
    assert body["code"] == original_code
    # Untouched metadata keys survive the update.
    assert body["metadata"]["address_detail"] == "1 Phố Huế"
    assert body["metadata"]["province_name"] == "Hà Nội"
    assert body["metadata"]["ward_name"] == "Phúc Tân"


@pytest.mark.asyncio
async def test_update_customer_clears_address_when_null_is_sent(
    client: AsyncClient,
    auth_headers: dict[str, str],
    customers,
):
    customer_id = await _customer_id_by_code(client, auth_headers)

    response = await client.patch(
        f"/api/v1/customers/{customer_id}",
        json={"province_name": None},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert "province_name" not in (response.json()["metadata"] or {})
    # The other address key is still there.
    assert response.json()["metadata"]["address_detail"] == "1 Phố Huế"


@pytest.mark.asyncio
async def test_update_customer_can_deactivate(client, auth_headers, customers):
    customer_id = await _customer_id_by_code(client, auth_headers)

    response = await client.patch(
        f"/api/v1/customers/{customer_id}",
        json={"is_active": False},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_update_customer_not_found(client, auth_headers):
    response = await client.patch(
        "/api/v1/customers/999999",
        json={"name": "Không tồn tại"},
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_viewer_without_create_permission_gets_403(client, viewer_headers):
    response = await client.post(
        "/api/v1/customers",
        json={"name": "Khách mới"},
        headers=viewer_headers,
    )
    assert response.status_code == 403
    assert response.json()["error_code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_viewer_without_update_permission_gets_403(client, viewer_headers, customers):
    listing = await client.get("/api/v1/customers", headers=viewer_headers)
    customer_id = listing.json()["items"][0]["id"]

    response = await client.patch(
        f"/api/v1/customers/{customer_id}",
        json={"name": "Đổi tên"},
        headers=viewer_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_viewer_with_view_permission_can_read(client, viewer_headers, customers):
    listing = await client.get("/api/v1/customers", headers=viewer_headers)
    assert listing.status_code == 200

    customer_id = listing.json()["items"][0]["id"]
    detail = await client.get(f"/api/v1/customers/{customer_id}", headers=viewer_headers)
    assert detail.status_code == 200


# ---------------------------------------------------------------------------
# Bill history
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_customer_bill_history_filters_by_role(client, auth_headers, activity):
    customer_id = activity["sender_id"]

    all_bills = await client.get(f"/api/v1/customers/{customer_id}/bills", headers=auth_headers)
    assert all_bills.status_code == 200
    assert all_bills.json()["total"] == 3

    as_sender = await client.get(
        f"/api/v1/customers/{customer_id}/bills",
        params={"role": "sender"},
        headers=auth_headers,
    )
    assert as_sender.json()["total"] == 2
    assert {b["tracking_number"] for b in as_sender.json()["items"]} == {"VD0001", "VD0003"}

    as_receiver = await client.get(
        f"/api/v1/customers/{customer_id}/bills",
        params={"role": "receiver"},
        headers=auth_headers,
    )
    assert as_receiver.json()["total"] == 1
    assert as_receiver.json()["items"][0]["tracking_number"] == "VD0002"


@pytest.mark.asyncio
async def test_customer_bill_history_paginates(client, auth_headers, activity):
    customer_id = activity["sender_id"]

    response = await client.get(
        f"/api/v1/customers/{customer_id}/bills",
        params={"page": 1, "page_size": 2},
        headers=auth_headers,
    )

    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert body["total"] == 3
    assert len(body["items"]) == 2


@pytest.mark.asyncio
async def test_customer_bill_history_not_found(client, auth_headers):
    response = await client.get("/api/v1/customers/999999/bills", headers=auth_headers)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_customer_metrics_counts_once_and_excludes_cancelled_revenue(
    client: AsyncClient,
    auth_headers: dict[str, str],
    activity,
):
    response = await client.get(
        f"/api/v1/customers/{activity['sender_id']}/metrics",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    # All three bills involve the customer.
    assert body["total_bills"] == 3
    assert body["delivered_bills"] == 1
    assert body["cancelled_bills"] == 1
    # Revenue: only bills where the customer is SENDER and not cancelled.
    # VD0001 (100.000) counts; VD0002 is receiver-only; VD0003 is cancelled.
    assert Decimal(body["total_revenue"]) == Decimal("100000.00")
    assert body["first_bill_at"] is not None
    assert body["last_bill_at"] is not None


@pytest.mark.asyncio
async def test_customer_metrics_zero_for_customer_without_bills(client, auth_headers, customers):
    listing = await client.get("/api/v1/customers", headers=auth_headers)
    customer_id = listing.json()["items"][0]["id"]

    response = await client.get(
        f"/api/v1/customers/{customer_id}/metrics",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_bills"] == 0
    assert Decimal(body["total_revenue"]) == Decimal("0")
    assert body["first_bill_at"] is None


@pytest.mark.asyncio
async def test_customer_metrics_not_found(client, auth_headers):
    response = await client.get("/api/v1/customers/999999/metrics", headers=auth_headers)
    assert response.status_code == 404
