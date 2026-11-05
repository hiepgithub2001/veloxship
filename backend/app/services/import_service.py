"""Excel import orchestration: validate an uploaded workbook, then commit it.

Flow (see ``docs/ke-hoach-module-import-excel.md`` §6.1):

1. ``validate_upload()`` — parse + normalise + validate every row and persist
   the verdict in ``import_rows``. **Nothing is written to bills/customers.**
2. ``commit_batch()`` — replay the usable rows through ``bill_service``, which
   keeps customer get-or-create, snapshots, status logs and audit intact.

The parsing rules themselves live in the pure ``app.services.importing``
package; this module only wires them to the database.
"""

from __future__ import annotations

import hashlib
import html
from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppError, ConflictError, NotFoundError
from app.core.timeutils import naive_utc
from app.crud import audit as audit_crud
from app.crud import import_batch as import_crud
from app.models.import_batch import ImportBatch, ImportRow
from app.models.province import Province
from app.models.user import User
from app.schemas.bill import BillContentLineSchema, BillCreate, BillParty, FeeBreakdown
from app.schemas.comment import CommentCreate
from app.services import bill_service, comment_service
from app.services.importing import (
    ImportOptions,
    RawRow,
    RowLimitExceeded,
    RowValidation,
    ValidationContext,
    build_province_index,
    detect_layout,
    iter_raw_rows,
    load_workbook_from_bytes,
    parse_options,
    validate_row,
)
from app.services.importing.validators import ERROR_DUPLICATE_TRACKING, STATUS_ERROR

MAX_FILE_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = (".xlsx",)
SOURCE_LAYOUT = "legacy_logex"
COMMIT_CHUNK_SIZE = 200
ERROR_ROW_FAILED = "IMPORT_ROW_FAILED"

STATUS_LABELS = {
    "ok": "Hợp lệ",
    "warning": "Cảnh báo",
    "error": "Lỗi",
    "imported": "Đã nhập",
    "skipped": "Bỏ qua",
}


def _app_error(
    code: str,
    message: str | None = None,
    *,
    details: dict | None = None,
    status_code: int = 400,
) -> AppError:
    """Build an ``AppError`` whose Vietnamese message may carry real values."""
    error = AppError(code, status_code=status_code, details=details)
    if message:
        error.message = message
    return error


async def _load_province_index(db: AsyncSession) -> dict[str, tuple[str, str]]:
    rows = (await db.execute(select(Province.code, Province.name))).all()
    return build_province_index([(code, name) for code, name in rows])


def _tracking_of(row: RawRow) -> str:
    from app.services.importing.validators import _tracking_value  # noqa: PLC0415

    return _tracking_value(row.cells)


async def validate_upload(
    db: AsyncSession,
    *,
    file_name: str,
    content: bytes,
    current_user: User,
    options_raw: dict | None = None,
) -> ImportBatch:
    """Parse and validate an uploaded workbook without writing business data."""
    if not file_name.lower().endswith(ALLOWED_EXTENSIONS):
        raise _app_error(
            "FILE_TYPE_NOT_ALLOWED", "Chỉ chấp nhận file .xlsx.", status_code=415
        )
    if not content:
        raise _app_error("IMPORT_FILE_REQUIRED")
    if len(content) > MAX_FILE_BYTES:
        raise _app_error("FILE_SIZE_EXCEEDED", "File vượt quá 5 MB.", status_code=413)

    options = parse_options(options_raw)
    file_hash = hashlib.sha256(content).hexdigest()

    try:
        workbook = load_workbook_from_bytes(content)
    except Exception as exc:  # noqa: BLE001 - openpyxl raises several types
        raise _app_error(
            "FILE_TYPE_NOT_ALLOWED",
            "File không đúng định dạng .xlsx hoặc bị hỏng.",
            status_code=415,
        ) from exc

    detection = detect_layout(workbook)
    if not detection.found:
        missing = ", ".join(detection.missing)
        raise _app_error(
            "IMPORT_COLUMNS_NOT_FOUND",
            f"Không nhận diện được cột dữ liệu. Thiếu: {missing}.",
            details={
                "sheet_name": detection.sheet_name,
                "header_row": detection.header_row,
                "missing": list(detection.missing),
                "found": sorted(detection.columns),
            },
        )

    province_index = await _load_province_index(db)
    if not province_index:
        raise _app_error(
            "IMPORT_PROVINCES_NOT_SEEDED",
            "Danh mục tỉnh/thành chưa được nạp. Chạy `make db-seed` trước khi import.",
        )

    try:
        raw_rows = iter_raw_rows(workbook, detection.layout, max_rows=options.max_rows)
    except RowLimitExceeded as exc:
        raise _app_error(
            "IMPORT_ROW_LIMIT_EXCEEDED",
            f"File vượt quá {exc.limit} dòng dữ liệu.",
        ) from exc

    if not raw_rows:
        raise _app_error("IMPORT_NOTHING_TO_IMPORT", "File không có dòng dữ liệu nào.")

    candidates = [
        tracking for tracking in (_tracking_of(row) for row in raw_rows) if tracking
    ]
    existing = await import_crud.get_existing_tracking_numbers(db, candidates)

    context = ValidationContext(
        provinces=province_index,
        existing_tracking=frozenset(existing),
        options=options,
    )

    seen: set[str] = set()
    validated: list[RowValidation] = []
    for raw_row in raw_rows:
        result = validate_row(raw_row, context)
        tracking = result.normalized.get("tracking_number")
        if tracking:
            if tracking in seen:
                result.warn(
                    f'Mã vận đơn "{tracking}" bị lặp trong cùng file — dòng này sẽ bị bỏ qua.',
                    code=ERROR_DUPLICATE_TRACKING,
                )
            seen.add(tracking)
        validated.append(result)

    batch = ImportBatch(
        entity_type="bill",
        file_name=file_name,
        file_hash=file_hash,
        source_layout=SOURCE_LAYOUT,
        status="validated",
        total_rows=len(validated),
        ok_rows=sum(1 for row in validated if row.status == "ok"),
        warning_rows=sum(1 for row in validated if row.status == "warning"),
        error_rows=sum(1 for row in validated if row.status == STATUS_ERROR),
        imported_rows=0,
        options={
            "catalogue_description": options.catalogue_description,
            "default_packages": options.default_packages,
            "normalize_names": options.normalize_names,
            "sender_name": options.sender_name,
            "sender_phone": options.sender_phone,
        },
        warnings=[],
        created_by=current_user.id,
    )

    previous = await import_crud.find_completed_batch_by_hash(db, file_hash)
    if previous is not None:
        batch.warnings = [
            f"File này đã được nhập trước đó (lần nhập #{previous.id}). "
            "Kiểm tra lại nếu bạn thật sự muốn nhập tiếp."
        ]

    rows = [
        ImportRow(
            row_number=row.row_number,
            raw_data={key: _jsonable(value) for key, value in row.raw.items()},
            normalized_data=row.normalized,
            status=row.status,
            error_code=row.error_code,
            error_message=row.error_message,
            warnings=row.warnings,
        )
        for row in validated
    ]

    await import_crud.create_batch(db, batch=batch, rows=rows)
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="import.batch_validated",
        entity_type="import_batch",
        entity_id=batch.id,
        details={
            "file_name": file_name,
            "total_rows": batch.total_rows,
            "error_rows": batch.error_rows,
        },
    )
    # No commit here: `get_db` owns the transaction boundary (see app/db/session.py).
    await db.flush()
    return batch


def _jsonable(value):
    """Make a cell value JSONB-safe (dates become ISO strings, everything else as-is)."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _contacts_html(extras: list[str]) -> str:
    items = "".join(f"<li>{html.escape(str(entry))}</li>" for entry in extras)
    return "<p><strong>Liên hệ khác (nhập từ Excel):</strong></p>" f"<ul>{items}</ul>"


async def _create_bill_from_row(
    db: AsyncSession,
    row: ImportRow,
    batch: ImportBatch,
    current_user: User,
):
    """Write one validated row through the normal bill service."""
    data = row.normalized_data or {}
    weight = Decimal(str(data.get("weight_kg", "0")))
    options = batch.options or {}
    description = options.get("catalogue_description") or "Catalogue"
    catalogue_quantity = data.get("catalogue_quantity")

    metadata: dict = {}
    if catalogue_quantity is not None:
        metadata["catalogue_quantity"] = int(catalogue_quantity)

    # Sender: column in the file -> per-import option -> company default.
    sender_name = data.get("sender_name") or settings.CARRIER_NAME
    sender_phone = data.get("sender_phone") or settings.CARRIER_HOTLINE

    payload = BillCreate(
        sender=BillParty(name=sender_name, phone=sender_phone),
        receiver=BillParty(
            name=data["receiver_name"],
            phone=data["contact_phone"],
            address_detail=data.get("address_detail") or None,
            province_code=data.get("province_code"),
            province_name=data.get("province_name"),
            province_raw=data.get("destination_raw"),
            contact_name=data.get("contact_name") or None,
            contact_raw=data.get("contact_raw") or None,
        ),
        cargo_type="goods",
        actual_weight_kg=float(weight),
        contents=[
            BillContentLineSchema(
                cargo_type="goods",
                description=description,
                quantity=int(data["packages"]),
                weight_kg=float(weight),
                metadata=metadata,
            )
        ],
        fee=FeeBreakdown(
            fee_main=0, fee_insurance=0, fee_other=0, fee_vat=0, fee_total=0
        ),
        payer="receiver",
        note=None,
    )

    bill = await bill_service.create_bill(
        db,
        payload,
        current_user.id,
        tracking_number=data["tracking_number"],
    )

    extras = data.get("extra_contacts") or []
    if extras:
        await comment_service.create_comment(
            db,
            CommentCreate(
                entity_type="bill",
                entity_id=bill.id,
                body=_contacts_html(extras),
                images=[],
            ),
            current_user,
        )
    return bill


async def commit_batch(
    db: AsyncSession,
    batch_id: int,
    *,
    current_user: User,
    skip_error_rows: bool = True,
) -> ImportBatch:
    """Write every usable row of a validated batch."""
    batch = await import_crud.get_batch(db, batch_id, with_rows=True)
    if batch is None:
        raise NotFoundError("IMPORT_BATCH_NOT_FOUND")
    if batch.status != "validated":
        raise ConflictError("IMPORT_BATCH_ALREADY_COMMITTED")

    usable = [
        row
        for row in batch.rows
        if row.status in ("ok", "warning")
        and row.error_code != ERROR_DUPLICATE_TRACKING
    ]
    if not usable:
        raise _app_error("IMPORT_NOTHING_TO_IMPORT", "Không có dòng hợp lệ để nhập.")

    # Remember which customer phones already existed so the result panel can
    # report how many new customers the import actually created.
    candidate_phones = sorted(
        {
            phone
            for phone in (
                [(row.normalized_data or {}).get("contact_phone") for row in usable]
                + [settings.CARRIER_HOTLINE]
            )
            if phone
        }
    )
    phones_before = await import_crud.get_existing_customer_phones(db, candidate_phones)

    batch.status = "committing"
    await db.flush()

    imported = 0
    failed = 0
    for index, row in enumerate(usable, start=1):
        try:
            async with db.begin_nested():
                bill = await _create_bill_from_row(db, row, batch, current_user)
            row.status = "imported"
            row.target_id = bill.id
            imported += 1
        except Exception as exc:  # noqa: BLE001 - one bad row must not kill the batch
            failed += 1
            row.status = "error"
            row.error_code = getattr(exc, "error_code", None) or ERROR_ROW_FAILED
            row.error_message = getattr(exc, "message", None) or str(exc)
        if index % COMMIT_CHUNK_SIZE == 0:
            await db.flush()

    for row in batch.rows:
        if row.status in ("ok", "warning") and row not in usable:
            row.status = "skipped"

    phones_after = await import_crud.get_existing_customer_phones(db, candidate_phones)
    batch.customers_created = len(phones_after - phones_before)
    batch.imported_rows = imported
    batch.status = "completed" if failed == 0 else "partially_completed"
    # DB timestamps are naive UTC (see app/core/timeutils.py).
    batch.committed_at = naive_utc(datetime.now(UTC))
    if failed:
        batch.error_message = f"{failed} dòng bị lỗi khi ghi dữ liệu."

    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="import.batch_committed",
        entity_type="import_batch",
        entity_id=batch.id,
        details={"imported_rows": imported, "failed_rows": failed},
    )
    # No commit here: `get_db` owns the transaction boundary.
    await db.flush()
    return await import_crud.get_batch(db, batch.id, with_rows=True)


async def build_result_xlsx(db: AsyncSession, batch: ImportBatch) -> BytesIO:
    """Render the original data plus a status/error column as a workbook."""
    rows = await import_crud.get_rows(db, batch.id)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Kết quả nhập"
    headers = [
        "Dòng",
        "Mã vận đơn",
        "Người gửi",
        "SĐT người gửi",
        "Khách nhận",
        "Tỉnh gốc",
        "Tỉnh chuẩn hoá",
        "Địa chỉ giao",
        "Người liên hệ",
        "SĐT",
        "Số kiện",
        "Trọng lượng (kg)",
        "SL Catalogue",
        "Trạng thái",
        "Lỗi / Cảnh báo",
        "Mã phiếu",
    ]
    sheet.append(headers)
    for cell in sheet[1]:
        cell.font = Font(bold=True)

    for row in rows:
        data = row.normalized_data or {}
        messages = list(row.warnings or [])
        if row.error_message:
            messages.insert(0, row.error_message)
        sheet.append(
            [
                row.row_number,
                data.get("tracking_number", ""),
                data.get("sender_name", ""),
                data.get("sender_phone", ""),
                data.get("receiver_name", ""),
                data.get("destination_raw", ""),
                data.get("province_name", ""),
                data.get("address_detail", ""),
                data.get("contact_name", ""),
                data.get("contact_phone", ""),
                data.get("packages", ""),
                float(data["weight_kg"]) if data.get("weight_kg") else "",
                data.get("catalogue_quantity", ""),
                STATUS_LABELS.get(row.status, row.status),
                " · ".join(messages),
                row.target_id or "",
            ]
        )

    widths = [8, 18, 18, 16, 28, 16, 18, 50, 18, 15, 10, 16, 14, 14, 60, 12]
    for index, width in enumerate(widths, start=1):
        sheet.column_dimensions[get_column_letter(index)].width = width

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


def options_for_batch(batch: ImportBatch) -> ImportOptions:
    """Rebuild the effective options of a batch (used by tests and callers)."""
    return parse_options(batch.options)
