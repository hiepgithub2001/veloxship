"""Integration tests for the dashboard summary API (GET /dashboard/summary).

Uses testcontainers[postgres] + asyncpg for real PostgreSQL testing, mirroring
the bill/vehicle integration-test setup.
"""

from datetime import UTC, datetime, time, timedelta
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
from app.models.permission import Role, RolePermission
from app.models.user import User
from app.services.dashboard_service import VN_TZ, vn_day_bounds


@pytest_asyncio.fixture(autouse=True)
async def _seed_roles(engine):
    """Seed default roles + a dashboard:view grant for `operator`."""
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
        session.add(RolePermission(role="operator", action="dashboard:view"))
        await session.commit()
    yield


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
            text(
                """
                CREATE OR REPLACE FUNCTION f_unaccent(text)
                RETURNS text AS $$
                SELECT public.unaccent('public.unaccent', $1)
                $$ LANGUAGE sql IMMUTABLE STRICT;
                """
            )
        )
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session


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
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_db, None)


async def _user_token(db_session: AsyncSession, username: str, role: str) -> dict[str, str]:
    user = User(
        username=username,
        full_name=username,
        password_hash="hashed",
        role=role,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = create_access_token(user.id, user.username)
    return {"Authorization": f"Bearer {token}"}


async def _add_bill(
    db_session: AsyncSession,
    *,
    tracking: str,
    status: str,
    created_at: datetime,
    province_code: str,
    fee_main: Decimal = Decimal("0.00"),
    cod_amount: Decimal = Decimal("0.00"),
    actor_id: int,
) -> Bill:
    sender = Customer(name="Gửi", customer_type="retail")
    receiver = Customer(name="Nhận", customer_type="retail")
    db_session.add_all([sender, receiver])
    await db_session.flush()

    bill = Bill(
        tracking_number=tracking,
        sender_id=sender.id,
        receiver_id=receiver.id,
        sender_snapshot={},
        receiver_snapshot={"province_code": province_code},
        cargo_type="goods",
        actual_weight_kg=Decimal("1.000"),
        chargeable_weight_kg=Decimal("1.000"),
        is_insurance_required=False,
        cod_amount=cod_amount,
        fee_main=fee_main,
        fee_insurance=Decimal("0.00"),
        fee_other=Decimal("0.00"),
        fee_vat=Decimal("0.00"),
        fee_total=fee_main,
        payer="sender",
        status=status,
        created_by=actor_id,
        updated_by=actor_id,
        created_at=created_at,
    )
    db_session.add(bill)
    await db_session.flush()
    return bill


def _at_vn(today, day_offset: int, hour: int = 9) -> datetime:
    """A naive-UTC timestamp for `day_offset` days before `today` at `hour` VN."""
    local = datetime.combine(today - timedelta(days=day_offset), time(hour), tzinfo=VN_TZ)
    return local.astimezone(UTC).replace(tzinfo=None)


@pytest.mark.asyncio
class TestDashboardSummary:
    async def test_summary_counts_and_buckets(self, client, db_session):
        days = 7
        start_date, today, _, _ = vn_day_bounds(days)

        token = await _user_token(db_session, "admin_dash", "admin")

        # 2 delivered + 1 in-transit today (Hà Nội), 1 cancelled 3 days ago (Hà Nội),
        # 1 in-transit today in Hồ Chí Minh.
        await _add_bill(
            db_session, tracking="D1", status="delivered",
            created_at=_at_vn(today, 0), province_code="1",
            fee_main=Decimal("1000.00"), actor_id=1,
        )
        await _add_bill(
            db_session, tracking="D2", status="delivered",
            created_at=_at_vn(today, 0), province_code="1",
            fee_main=Decimal("1000.00"), actor_id=1,
        )
        await _add_bill(
            db_session, tracking="D3", status="in_transit",
            created_at=_at_vn(today, 0), province_code="1",
            actor_id=1,
        )
        await _add_bill(
            db_session, tracking="D4", status="cancelled",
            created_at=_at_vn(today, 3), province_code="1",
            fee_main=Decimal("500.00"), actor_id=1,
        )
        await _add_bill(
            db_session, tracking="D5", status="in_transit",
            created_at=_at_vn(today, 0), province_code="79",
            actor_id=1,
        )
        await db_session.commit()

        resp = await client.get(f"/api/v1/dashboard/summary?days={days}", headers=token)
        assert resp.status_code == 200
        data = resp.json()

        assert data["range"]["days"] == days
        assert data["range"]["date_from"] == start_date.isoformat()
        assert data["range"]["date_to"] == today.isoformat()

        kpis = data["kpis"]
        assert kpis["total_bills"] == 5
        assert kpis["delivered_bills"] == 2
        assert kpis["cancelled_bills"] == 1
        assert kpis["in_progress_bills"] == 2
        assert kpis["delivery_rate"] == 40.0
        # cancelled bill is excluded from revenue → 1000 + 1000.
        assert kpis["revenue_total"] == "2000.00"
        assert kpis["bills_today"] == 4

        assert len(data["daily"]) == days
        assert data["daily"][-1]["date"] == today.isoformat()
        assert data["daily"][-1]["bills"] == 4
        assert data["daily"][-1]["revenue"] == "2000.00"

        status_counts = {item["status"]: item["count"] for item in data["status_counts"]}
        assert status_counts["delivered"] == 2
        assert status_counts["cancelled"] == 1
        assert status_counts["in_transit"] == 2

        by_code = {item["province_code"]: item for item in data["destinations"]}
        assert by_code["1"]["count"] == 4  # 2 delivered + 1 transit + 1 cancelled
        assert by_code["79"]["count"] == 1

    async def test_summary_enforces_dashboard_view(self, client, db_session):
        operator = await _user_token(db_session, "op_dash", "operator")
        shipper = await _user_token(db_session, "ship_dash", "shipper")

        ok = await client.get("/api/v1/dashboard/summary?days=7", headers=operator)
        assert ok.status_code == 200

        forbidden = await client.get("/api/v1/dashboard/summary?days=7", headers=shipper)
        assert forbidden.status_code == 403
        assert forbidden.json()["error_code"] == "FORBIDDEN"

    async def test_summary_rejects_invalid_days(self, client, db_session):
        token = await _user_token(db_session, "admin_days", "admin")
        for bad in (0, 6, 91, 100):
            resp = await client.get(f"/api/v1/dashboard/summary?days={bad}", headers=token)
            # Query validation failures surface as the app's 400 VALIDATION_ERROR.
            assert resp.status_code == 400, f"days={bad} should be rejected"
