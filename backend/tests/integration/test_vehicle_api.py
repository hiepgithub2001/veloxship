"""Integration tests for Vehicle API endpoints.

Uses testcontainers[postgres] + asyncpg for real PostgreSQL testing.
"""

from decimal import Decimal

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
from app.models.vehicle import Vehicle

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
async def db_session(engine):
    """Provide a test database session."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


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
async def auth_headers(admin_user: User) -> dict[str, str]:
    """Generate JWT auth headers for the admin user."""
    token = create_access_token(admin_user.id, admin_user.username)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def driver_user(db_session: AsyncSession) -> User:
    """Create a driver user for vehicle assignment."""
    user = User(
        username="driver01",
        full_name="Nguyễn Văn Tài Xế",
        password_hash="hashed",
        role="shipper",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def inactive_driver(db_session: AsyncSession) -> User:
    """Create an inactive driver user."""
    user = User(
        username="driver_inactive",
        full_name="Tài Xế Nghỉ Việc",
        password_hash="hashed",
        role="shipper",
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def depot(db_session: AsyncSession) -> Depot:
    """Create a test depot."""
    d = Depot(
        code="BC-Q1",
        name="Bưu cục Quận 1",
        phone="0901234567",
        address_detail="123 Nguyễn Huệ",
    )
    db_session.add(d)
    await db_session.commit()
    await db_session.refresh(d)
    return d


@pytest_asyncio.fixture
async def depot2(db_session: AsyncSession) -> Depot:
    """Create a second test depot."""
    d = Depot(
        code="BC-Q7",
        name="Bưu cục Quận 7",
        phone="0907654321",
        address_detail="456 Nguyễn Thị Thập",
    )
    db_session.add(d)
    await db_session.commit()
    await db_session.refresh(d)
    return d


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def vehicle_payload(
    license_plate: str = "51C-123.45",
    vehicle_type: str = "truck",
    max_weight_kg: str = "5000.000",
    max_volume_m3: str = "20.50",
    driver_id: int | None = None,
    latest_depot_id: int | None = None,
    status: str | None = None,
) -> dict:
    """Build a vehicle creation payload."""
    payload: dict = {
        "license_plate": license_plate,
        "vehicle_type": vehicle_type,
        "max_weight_kg": max_weight_kg,
        "max_volume_m3": max_volume_m3,
    }
    if driver_id is not None:
        payload["driver_id"] = driver_id
    if latest_depot_id is not None:
        payload["latest_depot_id"] = latest_depot_id
    if status is not None:
        payload["status"] = status
    return payload


# ---------------------------------------------------------------------------
# Test: Full CRUD flow (create → list → update → soft-delete)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestCRUDFlow:
    """Test full CRUD lifecycle of a vehicle."""

    async def test_create_vehicle(self, client: AsyncClient, auth_headers: dict):
        """Create a vehicle and verify response fields."""
        payload = vehicle_payload()
        resp = await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)

        assert resp.status_code == 201
        data = resp.json()
        assert data["license_plate"] == "51C-123.45"
        assert data["vehicle_type"] == "truck"
        assert data["status"] == "active"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_list_vehicles_after_create(self, client: AsyncClient, auth_headers: dict):
        """List vehicles after creating one."""
        payload = vehicle_payload(license_plate="51C-LIST.01")
        await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)

        resp = await client.get("/api/v1/vehicles", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        plates = [item["license_plate"] for item in data["items"]]
        assert "51C-LIST.01" in plates

    async def test_update_vehicle(self, client: AsyncClient, auth_headers: dict):
        """Update a vehicle's license plate."""
        create_resp = await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(license_plate="51C-UPD.01"),
            headers=auth_headers,
        )
        vehicle_id = create_resp.json()["id"]

        update_resp = await client.patch(
            f"/api/v1/vehicles/{vehicle_id}",
            json={"license_plate": "51C-UPD.99"},
            headers=auth_headers,
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["license_plate"] == "51C-UPD.99"

    async def test_soft_delete_vehicle(self, client: AsyncClient, auth_headers: dict):
        """Soft-delete sets status to inactive."""
        create_resp = await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(license_plate="51C-DEL.01"),
            headers=auth_headers,
        )
        vehicle_id = create_resp.json()["id"]

        delete_resp = await client.patch(
            f"/api/v1/vehicles/{vehicle_id}",
            json={"status": "inactive"},
            headers=auth_headers,
        )
        assert delete_resp.status_code == 200
        assert delete_resp.json()["status"] == "inactive"


# ---------------------------------------------------------------------------
# Test: Search (case-insensitive on license_plate)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestSearch:
    """Test search functionality on license_plate."""

    async def test_search_case_insensitive(self, client: AsyncClient, auth_headers: dict):
        """Search is case-insensitive on license_plate."""
        await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(license_plate="51C-ABC.12"),
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(license_plate="30A-XYZ.99"),
            headers=auth_headers,
        )

        # Search with lowercase
        resp = await client.get(
            "/api/v1/vehicles", params={"search": "abc"}, headers=auth_headers
        )
        data = resp.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert "abc" in item["license_plate"].lower()

    async def test_search_uppercase(self, client: AsyncClient, auth_headers: dict):
        """Search with uppercase also matches."""
        await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(license_plate="51c-srch.up"),
            headers=auth_headers,
        )

        resp = await client.get(
            "/api/v1/vehicles", params={"search": "SRCH"}, headers=auth_headers
        )
        data = resp.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert "srch" in item["license_plate"].lower()

    async def test_search_partial_match(self, client: AsyncClient, auth_headers: dict):
        """Search matches partial substrings."""
        await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(license_plate="51C-PART.45"),
            headers=auth_headers,
        )

        resp = await client.get(
            "/api/v1/vehicles", params={"search": "PART"}, headers=auth_headers
        )
        assert resp.json()["total"] >= 1

    async def test_search_no_match(self, client: AsyncClient, auth_headers: dict):
        """Search returns empty when no match."""
        resp = await client.get(
            "/api/v1/vehicles", params={"search": "ZZZNOMATCH"}, headers=auth_headers
        )
        assert resp.json()["total"] == 0
        assert resp.json()["items"] == []


# ---------------------------------------------------------------------------
# Test: Filter combinations (status + vehicle_type + latest_depot_id)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestFilters:
    """Test filter combinations with AND logic."""

    async def test_filter_by_status(self, client: AsyncClient, auth_headers: dict):
        """Filter by status returns only matching vehicles."""
        await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(license_plate="51C-FS.01", status="maintenance"),
            headers=auth_headers,
        )

        resp = await client.get(
            "/api/v1/vehicles", params={"status": "maintenance"}, headers=auth_headers
        )
        data = resp.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert item["status"] == "maintenance"

    async def test_filter_by_vehicle_type(self, client: AsyncClient, auth_headers: dict):
        """Filter by vehicle_type."""
        await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(
                license_plate="51C-FT.01",
                vehicle_type="motorcycle",
                max_weight_kg="100.000",
                max_volume_m3="1.50",
            ),
            headers=auth_headers,
        )

        resp = await client.get(
            "/api/v1/vehicles", params={"vehicle_type": "motorcycle"}, headers=auth_headers
        )
        data = resp.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert item["vehicle_type"] == "motorcycle"

    async def test_filter_by_depot(
        self, client: AsyncClient, auth_headers: dict, depot: Depot
    ):
        """Filter by latest_depot_id."""
        await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(license_plate="51C-FD.01", latest_depot_id=depot.id),
            headers=auth_headers,
        )

        resp = await client.get(
            "/api/v1/vehicles",
            params={"latest_depot_id": depot.id},
            headers=auth_headers,
        )
        data = resp.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert item["latest_depot_id"] == depot.id

    async def test_filter_combination_and_logic(
        self, client: AsyncClient, auth_headers: dict, depot: Depot
    ):
        """Multiple filters combine with AND logic."""
        # Active truck at depot
        await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(
                license_plate="51C-AND.01",
                vehicle_type="truck",
                status="active",
                latest_depot_id=depot.id,
            ),
            headers=auth_headers,
        )
        # Active motorcycle at depot
        await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(
                license_plate="51C-AND.02",
                vehicle_type="motorcycle",
                max_weight_kg="100.000",
                max_volume_m3="1.50",
                status="active",
                latest_depot_id=depot.id,
            ),
            headers=auth_headers,
        )
        # Inactive truck at depot
        await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(
                license_plate="51C-AND.03",
                vehicle_type="truck",
                status="inactive",
                latest_depot_id=depot.id,
            ),
            headers=auth_headers,
        )

        # Filter: active + truck + at depot
        resp = await client.get(
            "/api/v1/vehicles",
            params={
                "status": "active",
                "vehicle_type": "truck",
                "latest_depot_id": depot.id,
            },
            headers=auth_headers,
        )
        data = resp.json()
        # Should match at least the one active truck at depot
        assert data["total"] >= 1
        for item in data["items"]:
            assert item["status"] == "active"
            assert item["vehicle_type"] == "truck"
            assert item["latest_depot_id"] == depot.id


# ---------------------------------------------------------------------------
# Test: Pagination parameters and metadata
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestPagination:
    """Test pagination behavior and metadata."""

    async def test_default_pagination(self, client: AsyncClient, auth_headers: dict):
        """Default page=1, page_size=20."""
        await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(license_plate="51C-PG.00"),
            headers=auth_headers,
        )

        resp = await client.get("/api/v1/vehicles", headers=auth_headers)
        data = resp.json()
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total"] >= 1

    async def test_custom_page_size(self, client: AsyncClient, auth_headers: dict):
        """Custom page_size limits items returned."""
        for i in range(5):
            await client.post(
                "/api/v1/vehicles",
                json=vehicle_payload(license_plate=f"51C-PS{i:02d}.00"),
                headers=auth_headers,
            )

        resp = await client.get(
            "/api/v1/vehicles", params={"page_size": 2}, headers=auth_headers
        )
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] >= 5
        assert data["page_size"] == 2

    async def test_page_navigation(self, client: AsyncClient, auth_headers: dict):
        """Page 2 returns correct subset."""
        for i in range(5):
            await client.post(
                "/api/v1/vehicles",
                json=vehicle_payload(license_plate=f"51C-PN{i:02d}.00"),
                headers=auth_headers,
            )

        resp = await client.get(
            "/api/v1/vehicles", params={"page": 2, "page_size": 2}, headers=auth_headers
        )
        data = resp.json()
        assert len(data["items"]) <= 2
        assert data["page"] == 2

    async def test_empty_page_returns_empty_items(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Page beyond total returns empty items."""
        resp = await client.get(
            "/api/v1/vehicles", params={"page": 9999}, headers=auth_headers
        )
        data = resp.json()
        assert data["items"] == []

    async def test_invalid_page_size_rejected(
        self, client: AsyncClient, auth_headers: dict
    ):
        """page_size > 100 returns 422."""
        resp = await client.get(
            "/api/v1/vehicles", params={"page_size": 200}, headers=auth_headers
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Test: driver_name and depot_name resolution
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestNameResolution:
    """Test that driver_name and depot_name are resolved in responses."""

    async def test_driver_name_resolved(
        self,
        client: AsyncClient,
        auth_headers: dict,
        driver_user: User,
    ):
        """Response includes driver_name from users table."""
        payload = vehicle_payload(
            license_plate="51C-DRV.01", driver_id=driver_user.id
        )
        resp = await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)

        assert resp.status_code == 201
        data = resp.json()
        assert data["driver_id"] == driver_user.id
        assert data["driver_name"] == "Nguyễn Văn Tài Xế"

    async def test_depot_name_resolved(
        self,
        client: AsyncClient,
        auth_headers: dict,
        depot: Depot,
    ):
        """Response includes depot_name from depots table."""
        payload = vehicle_payload(
            license_plate="51C-DPT.01", latest_depot_id=depot.id
        )
        resp = await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)

        assert resp.status_code == 201
        data = resp.json()
        assert data["latest_depot_id"] == depot.id
        assert data["depot_name"] == "Bưu cục Quận 1"

    async def test_both_names_in_list(
        self,
        client: AsyncClient,
        auth_headers: dict,
        driver_user: User,
        depot: Depot,
    ):
        """Both driver_name and depot_name are resolved in list response."""
        payload = vehicle_payload(
            license_plate="51C-BOTH.01",
            driver_id=driver_user.id,
            latest_depot_id=depot.id,
        )
        await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)

        resp = await client.get(
            "/api/v1/vehicles", params={"search": "BOTH"}, headers=auth_headers
        )
        data = resp.json()
        assert data["total"] >= 1
        item = next(i for i in data["items"] if i["license_plate"] == "51C-BOTH.01")
        assert item["driver_name"] == "Nguyễn Văn Tài Xế"
        assert item["depot_name"] == "Bưu cục Quận 1"

    async def test_null_driver_depot_names(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Null driver_id/depot_id results in null names."""
        payload = vehicle_payload(license_plate="51C-NUL.01")
        resp = await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)

        data = resp.json()
        assert data["driver_id"] is None
        assert data["driver_name"] is None
        assert data["latest_depot_id"] is None
        assert data["depot_name"] is None


# ---------------------------------------------------------------------------
# Test: Error responses
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestErrors:
    """Test error responses for various invalid scenarios."""

    async def test_duplicate_license_plate_on_create(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Creating a vehicle with existing license_plate returns 409."""
        payload = vehicle_payload(license_plate="51C-DUP.01")
        await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)

        # Second create with same plate
        resp = await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)
        assert resp.status_code == 409
        data = resp.json()
        assert data["error_code"] == "LICENSE_PLATE_EXISTS"

    async def test_duplicate_license_plate_on_update(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Updating to an existing license_plate on another vehicle returns 409."""
        r1 = await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(license_plate="51C-DU1.01"),
            headers=auth_headers,
        )
        r2 = await client.post(
            "/api/v1/vehicles",
            json=vehicle_payload(license_plate="51C-DU2.02"),
            headers=auth_headers,
        )
        vehicle2_id = r2.json()["id"]

        # Try to update vehicle2's plate to vehicle1's plate
        resp = await client.patch(
            f"/api/v1/vehicles/{vehicle2_id}",
            json={"license_plate": "51C-DU1.01"},
            headers=auth_headers,
        )
        assert resp.status_code == 409

    async def test_vehicle_not_found(self, client: AsyncClient, auth_headers: dict):
        """Updating non-existent vehicle returns 404."""
        resp = await client.patch(
            "/api/v1/vehicles/99999",
            json={"status": "inactive"},
            headers=auth_headers,
        )
        assert resp.status_code == 404
        assert resp.json()["error_code"] == "VEHICLE_NOT_FOUND"

    async def test_invalid_driver_id(self, client: AsyncClient, auth_headers: dict):
        """Creating with non-existent driver_id returns 422."""
        payload = vehicle_payload(license_plate="51C-ERR.01", driver_id=99999)
        resp = await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)

        assert resp.status_code == 422
        assert resp.json()["error_code"] == "DRIVER_NOT_FOUND"

    async def test_inactive_driver_id(
        self, client: AsyncClient, auth_headers: dict, inactive_driver: User
    ):
        """Creating with inactive driver returns 422."""
        payload = vehicle_payload(
            license_plate="51C-ERR.02", driver_id=inactive_driver.id
        )
        resp = await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)

        assert resp.status_code == 422
        assert resp.json()["error_code"] == "DRIVER_NOT_FOUND"

    async def test_invalid_depot_id(self, client: AsyncClient, auth_headers: dict):
        """Creating with non-existent depot_id returns 422."""
        payload = vehicle_payload(license_plate="51C-ERR.03", latest_depot_id=99999)
        resp = await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)

        assert resp.status_code == 422
        assert resp.json()["error_code"] == "DEPOT_NOT_FOUND"

    async def test_unauthenticated_request(self, client: AsyncClient):
        """Request without auth returns 401/403."""
        resp = await client.get("/api/v1/vehicles")
        assert resp.status_code in (401, 403)
