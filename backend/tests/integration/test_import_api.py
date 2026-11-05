"""Integration tests for the Excel import API.

Uses testcontainers[postgres] + asyncpg, following the fixture pattern of
``tests/integration/test_bill_api.py`` (this repo has no shared conftest).

The golden input is the customer's real workbook, copied to
``tests/fixtures/import-mr-hai-logex.xlsx``. Its expected outcome is documented
in ``docs/templates/du-lieu-mau-va-ket-qua-mong-doi.xlsx``.
"""

from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from openpyxl import Workbook
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.security import create_access_token
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.bill import Bill
from app.models.bill_content_line import BillContentLine
from app.models.comment import Comment
from app.models.customer import Customer
from app.models.user import User
from app.services.importing.locations import PROVINCES

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "import-mr-hai-logex.xlsx"

XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
IMPORT_URL = "/api/v1/imports"


postgres_container = PostgresContainer("postgres:16-alpine", driver="asyncpg")


def get_async_database_url() -> str:
    host = postgres_container.get_container_host_ip()
    port = postgres_container.get_exposed_port(5432)
    return (
        f"postgresql+asyncpg://{postgres_container.username}:"
        f"{postgres_container.password}@{host}:{port}/{postgres_container.dbname}"
    )


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
        await conn.execute(text("""
                CREATE OR REPLACE FUNCTION f_unaccent(text)
                RETURNS text AS $$
                SELECT public.unaccent('public.unaccent', $1)
                $$ LANGUAGE sql IMMUTABLE STRICT;
                """))
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text("CREATE SEQUENCE IF NOT EXISTS bill_tracking_seq START 1 CACHE 50")
        )
        await conn.execute(
            text("CREATE SEQUENCE IF NOT EXISTS customer_code_seq START 1 CACHE 50")
        )
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _seed_roles_and_provinces(engine):
    """Roles satisfy the users.role FK; provinces feed the destination resolver."""
    from app.models.permission import Role
    from app.models.province import Province

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
        for code, name in PROVINCES:
            session.add(Province(code=code, name=name))
        await session.commit()
    yield


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


async def _create_user(db_session: AsyncSession, username: str, role: str) -> User:
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
    return user


@pytest_asyncio.fixture
async def auth_headers(db_session: AsyncSession) -> dict[str, str]:
    user = await _create_user(db_session, "admin_importer", "admin")
    token = create_access_token(user.id, user.username)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def no_permission_headers(db_session: AsyncSession) -> dict[str, str]:
    """A shipper holds no `bill:import` permission row."""
    user = await _create_user(db_session, "shipper_no_import", "shipper")
    token = create_access_token(user.id, user.username)
    return {"Authorization": f"Bearer {token}"}


def _workbook_bytes(header: list[str], row: list) -> bytes:
    from io import BytesIO

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sheet1"
    sheet.append(header)
    sheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _upload(
    client: AsyncClient, content: bytes, headers: dict[str, str], name: str = "x.xlsx"
):
    return client.post(
        IMPORT_URL,
        files={"file": (name, content, XLSX)},
        headers=headers,
    )


@pytest.mark.asyncio
class TestValidate:
    async def test_validate_returns_summary_and_preview(self, client, auth_headers):
        response = _upload(client, FIXTURE.read_bytes(), auth_headers, "mr-hai.xlsx")
        assert response.status_code == 201, response.text

        body = response.json()
        assert body["status"] == "validated"
        assert body["source_layout"] == "legacy_logex"
        assert body["summary"]["total_rows"] == 70
        assert body["summary"]["error_rows"] == 0
        assert body["summary"]["ok_rows"] + body["summary"]["warning_rows"] == 70
        assert len(body["preview"]) == 70

        first = body["preview"][0]
        assert first["row_number"] == 3
        assert first["normalized_data"]["tracking_number"] == "HNLG5"
        assert first["normalized_data"]["province_name"] == "Hà Nội"
        assert first["normalized_data"]["packages"] == 3
        assert first["normalized_data"]["weight_kg"] == "43.500"
        assert first["normalized_data"]["catalogue_quantity"] == 150

    async def test_validate_warns_about_the_two_contact_rows(
        self, client, auth_headers
    ):
        body = _upload(client, FIXTURE.read_bytes(), auth_headers).json()
        with_extras = [
            row
            for row in body["preview"]
            if row["normalized_data"].get("extra_contacts")
        ]
        assert len(with_extras) == 12

    async def test_validate_converts_merged_provinces(self, client, auth_headers):
        body = _upload(client, FIXTURE.read_bytes(), auth_headers).json()
        hai_duong = [
            row
            for row in body["preview"]
            if row["normalized_data"].get("destination_raw") == "Hải Dương"
        ]
        assert hai_duong, "the fixture contains Hải Dương rows"
        for row in hai_duong:
            assert row["normalized_data"]["province_name"] == "Hải Phòng"
            assert row["status"] == "warning"

    async def test_validate_reports_missing_columns(self, client, auth_headers):
        content = _workbook_bytes(["Mã đơn", "Ghi chú"], ["HNLG1", "x"])
        response = _upload(client, content, auth_headers)
        assert response.status_code == 400
        assert response.json()["error_code"] == "IMPORT_COLUMNS_NOT_FOUND"

    async def test_validate_rejects_non_xlsx(self, client, auth_headers):
        response = _upload(client, b"not-a-workbook", auth_headers, "x.csv")
        assert response.status_code == 415

    async def test_validate_requires_the_import_permission(
        self, client, no_permission_headers
    ):
        response = _upload(client, FIXTURE.read_bytes(), no_permission_headers)
        assert response.status_code == 403


@pytest.mark.asyncio
class TestCommit:
    async def test_commit_writes_bills_lines_and_comments(
        self, client, auth_headers, db_session: AsyncSession
    ):
        created = _upload(client, FIXTURE.read_bytes(), auth_headers).json()
        response = await client.post(
            f"{IMPORT_URL}/{created['id']}/commit",
            json={"skip_error_rows": True},
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["status"] == "completed"
        assert body["summary"]["imported_rows"] == 70

        bill_count = (
            await db_session.execute(select(func.count()).select_from(Bill))
        ).scalar_one()
        assert bill_count == 70

        customer_count = (
            await db_session.execute(select(func.count()).select_from(Customer))
        ).scalar_one()
        # 69 distinct receivers + the default sender company = 70?  The sender
        # phone is shared with one of them only if it collides, which it does not.
        assert customer_count == 70

        comment_count = (
            await db_session.execute(select(func.count()).select_from(Comment))
        ).scalar_one()
        assert comment_count == 12

        bill = (
            await db_session.execute(
                select(Bill).where(Bill.tracking_number == "HNLG5")
            )
        ).scalar_one()
        assert bill.receiver_snapshot["name"] == "HẰNG HÒA"
        assert bill.receiver_snapshot["province_name"] == "Hà Nội"
        assert bill.receiver_snapshot["province_raw"] == "Hà Nội"
        assert (
            bill.receiver_snapshot["address_detail"]
            == "B2 10 Shop house 24H Đường Tố Hữu, Phường Hà Đông, Hà Nội."
        )
        assert bill.cargo_type == "goods"
        assert bill.payer == "receiver"
        assert bill.fee_total == 0
        assert float(bill.actual_weight_kg) == pytest.approx(43.5)

        line = (
            await db_session.execute(
                select(BillContentLine).where(BillContentLine.bill_id == bill.id)
            )
        ).scalar_one()
        assert line.quantity == 3  # Số kiện
        assert float(line.weight_kg) == pytest.approx(43.5)
        assert line.metadata_["catalogue_quantity"] == 150  # "thông tin thêm"
        assert line.description == "Catalogue"

    async def test_commit_keeps_the_customer_contact_person(
        self, client, auth_headers, db_session: AsyncSession
    ):
        created = _upload(client, FIXTURE.read_bytes(), auth_headers).json()
        await client.post(
            f"{IMPORT_URL}/{created['id']}/commit", json={}, headers=auth_headers
        )
        customer = (
            await db_session.execute(
                select(Customer).where(Customer.phone == "0949988999")
            )
        ).scalar_one()
        assert customer.name == "HẰNG HÒA"
        assert customer.customer_metadata["contact_name"] == "Hương"
        assert customer.customer_metadata["contact_raw"] == "Chị Hương: 0949988999"

    async def test_second_contact_becomes_a_comment(
        self, client, auth_headers, db_session: AsyncSession
    ):
        created = _upload(client, FIXTURE.read_bytes(), auth_headers).json()
        await client.post(
            f"{IMPORT_URL}/{created['id']}/commit", json={}, headers=auth_headers
        )
        bill = (
            await db_session.execute(
                select(Bill).where(Bill.tracking_number == "HNLG10")
            )
        ).scalar_one()
        comment = (
            await db_session.execute(
                select(Comment).where(
                    Comment.entity_type == "bill", Comment.entity_id == bill.id
                )
            )
        ).scalar_one()
        assert "Liên hệ khác" in comment.body
        assert "Ngọc" in comment.body
        assert "0973319660" in comment.body

    async def test_reimporting_the_same_file_imports_nothing(
        self, client, auth_headers
    ):
        created = _upload(client, FIXTURE.read_bytes(), auth_headers).json()
        await client.post(
            f"{IMPORT_URL}/{created['id']}/commit", json={}, headers=auth_headers
        )

        second = _upload(client, FIXTURE.read_bytes(), auth_headers).json()
        assert second["warnings"], "duplicate file must be flagged"
        assert all(
            row["error_code"] == "IMPORT_DUPLICATE_TRACKING"
            for row in second["preview"]
        )

        response = await client.post(
            f"{IMPORT_URL}/{second['id']}/commit", json={}, headers=auth_headers
        )
        assert response.status_code == 400
        assert response.json()["error_code"] == "IMPORT_NOTHING_TO_IMPORT"

    async def test_commit_twice_is_rejected(self, client, auth_headers):
        created = _upload(client, FIXTURE.read_bytes(), auth_headers).json()
        first = await client.post(
            f"{IMPORT_URL}/{created['id']}/commit", json={}, headers=auth_headers
        )
        assert first.status_code == 200
        second = await client.post(
            f"{IMPORT_URL}/{created['id']}/commit", json={}, headers=auth_headers
        )
        assert second.status_code == 409
        assert second.json()["error_code"] == "IMPORT_BATCH_ALREADY_COMMITTED"

    async def test_result_workbook_can_be_downloaded(self, client, auth_headers):
        created = _upload(client, FIXTURE.read_bytes(), auth_headers).json()
        response = await client.get(
            f"{IMPORT_URL}/{created['id']}/result", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith(XLSX)
        assert len(response.content) > 1000


@pytest.mark.asyncio
class TestHistory:
    async def test_rows_can_be_filtered_and_paginated(self, client, auth_headers):
        created = _upload(client, FIXTURE.read_bytes(), auth_headers).json()
        response = await client.get(
            f"{IMPORT_URL}/{created['id']}/rows",
            params={"status": "warning", "page": 1, "page_size": 10},
            headers=auth_headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["page"] == 1
        assert body["page_size"] == 10
        assert all(item["status"] == "warning" for item in body["items"])

    async def test_history_lists_the_batch(self, client, auth_headers):
        _upload(client, FIXTURE.read_bytes(), auth_headers)
        response = await client.get(IMPORT_URL, headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["file_name"] == "x.xlsx"

    async def test_missing_batch_returns_404(self, client, auth_headers):
        response = await client.get(f"{IMPORT_URL}/999999", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["error_code"] == "IMPORT_BATCH_NOT_FOUND"
