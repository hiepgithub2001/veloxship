"""Imports API — bulk import of bills from an Excel workbook.

Three-step flow: ``POST /imports`` validates and stores a preview, ``GET
/imports/{id}`` lets the user inspect it, ``POST /imports/{id}/commit`` writes
the usable rows. Nothing touches ``bills`` before the commit.
"""

from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import require_permission
from app.core.exceptions import AppError
from app.crud import import_batch as import_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.import_batch import (
    ImportBatchPage,
    ImportBatchRead,
    ImportCommitRequest,
    ImportRowPage,
    ImportRowRead,
)
from app.services import import_service

router = APIRouter(prefix="/imports", tags=["imports"])

_XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

CurrentUser = Annotated[User, Depends(require_permission("bill:import"))]
DbSession = Annotated[AsyncSession, Depends(get_db)]


def _parse_options(raw: str | None) -> dict | None:
    """Decode the optional JSON ``options`` form field."""
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AppError(
            "VALIDATION_ERROR", details={"options": "JSON không hợp lệ."}
        ) from exc
    if not isinstance(parsed, dict):
        raise AppError("VALIDATION_ERROR", details={"options": "Phải là JSON object."})
    return parsed


@router.post("", response_model=ImportBatchRead, status_code=201)
async def create_import(
    file: Annotated[UploadFile, File()],
    db: DbSession,
    current_user: CurrentUser,
    options: Annotated[str | None, Form()] = None,
):
    """Upload a workbook, validate every row and return the preview."""
    content = await file.read()
    batch = await import_service.validate_upload(
        db,
        file_name=file.filename or "import.xlsx",
        content=content,
        current_user=current_user,
        options_raw=_parse_options(options),
    )
    return ImportBatchRead.from_model(batch, preview=batch.rows)


@router.get("", response_model=ImportBatchPage)
async def list_imports(
    db: DbSession,
    current_user: CurrentUser,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Return the import history, newest first."""
    items, total = await import_crud.list_batches(db, page=page, page_size=page_size)
    return ImportBatchPage(
        items=[ImportBatchRead.from_model(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{batch_id}", response_model=ImportBatchRead)
async def get_import(batch_id: int, db: DbSession, current_user: CurrentUser):
    """Return one batch with its summary and preview."""
    batch = await import_crud.get_batch(db, batch_id, with_rows=True)
    if batch is None:
        raise AppError("IMPORT_BATCH_NOT_FOUND", status_code=404)
    return ImportBatchRead.from_model(batch, preview=batch.rows)


@router.get("/{batch_id}/rows", response_model=ImportRowPage)
async def list_import_rows(
    batch_id: int,
    db: DbSession,
    current_user: CurrentUser,
    status: Annotated[str | None, Query(max_length=20)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 50,
):
    """Return a page of a batch's rows, filterable by status."""
    batch = await import_crud.get_batch(db, batch_id)
    if batch is None:
        raise AppError("IMPORT_BATCH_NOT_FOUND", status_code=404)
    items, total = await import_crud.list_rows(
        db, batch_id, status=status, page=page, page_size=page_size
    )
    return ImportRowPage(
        items=[ImportRowRead.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post("/{batch_id}/commit", response_model=ImportBatchRead)
async def commit_import(
    batch_id: int,
    db: DbSession,
    current_user: CurrentUser,
    body: ImportCommitRequest | None = None,
):
    """Write the usable rows of a validated batch."""
    payload = body or ImportCommitRequest()
    batch = await import_service.commit_batch(
        db,
        batch_id,
        current_user=current_user,
        skip_error_rows=payload.skip_error_rows,
    )
    return ImportBatchRead.from_model(batch, preview=batch.rows)


@router.get("/{batch_id}/result")
async def download_import_result(
    batch_id: int, db: DbSession, current_user: CurrentUser
):
    """Download the import result as an .xlsx file."""
    batch = await import_crud.get_batch(db, batch_id)
    if batch is None:
        raise AppError("IMPORT_BATCH_NOT_FOUND", status_code=404)
    buffer = await import_service.build_result_xlsx(db, batch)
    return Response(
        content=buffer.getvalue(),
        media_type=_XLSX_MEDIA_TYPE,
        headers={
            "Content-Disposition": f'attachment; filename="import-result-{batch_id}.xlsx"'
        },
    )
