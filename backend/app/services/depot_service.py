"""Depot business logic — create, update with validation."""

import structlog
from fastapi import UploadFile

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, ConflictError, NotFoundError
from app.crud import depot as depot_crud
from app.models.depot import Depot
from app.models.ward import Ward
from app.schemas.depot import DepotCreate, DepotUpdate
from app.services.storage_service import upload_file

logger = structlog.get_logger()


async def _validate_ward_code(db: AsyncSession, ward_code: str) -> None:
    """Raise AppError(WARD_NOT_FOUND) if ward_code does not exist."""
    result = await db.execute(select(Ward.code).where(Ward.code == ward_code))
    if result.scalar_one_or_none() is None:
        raise AppError("WARD_NOT_FOUND", status_code=422)


async def _upload_images(images: list[UploadFile], entity: str) -> list[str]:
    """Upload images to S3 and return list of S3 keys."""
    keys: list[str] = []
    for file in images:
        result = await upload_file(file)
        keys.append(result.key)
    logger.info("images.uploaded", entity=entity, count=len(keys))
    return keys


async def create_depot(
    db: AsyncSession, payload: DepotCreate, images: list[UploadFile] | None = None
) -> Depot:
    """Create a depot after checking code uniqueness and ward existence."""
    # 1. Check code uniqueness
    existing = await depot_crud.get_depot_by_code(db, payload.code)
    if existing is not None:
        raise ConflictError("DEPOT_CODE_EXISTS")

    # 2. Validate ward_code exists if provided
    if payload.ward_code:
        await _validate_ward_code(db, payload.ward_code)

    # 3. Upload images if provided, merge with any pre-existing keys
    new_keys = await _upload_images(images, "depot") if images else []
    base_urls = list(payload.image_urls or [])
    base_urls.extend(new_keys)

    # 4. Build final payload with image_urls
    final_payload = payload.model_copy(update={"image_urls": base_urls})

    # 5. Delegate to CRUD
    return await depot_crud.create_depot(db, payload=final_payload)


async def update_depot(
    db: AsyncSession,
    depot_id: int,
    payload: DepotUpdate,
    images: list[UploadFile] | None = None,
) -> Depot:
    """Update a depot with ward validation and is_active idempotency."""
    # 1. Get depot or raise NotFoundError
    depot = await depot_crud.get_depot(db, depot_id)
    if depot is None:
        raise NotFoundError("DEPOT_NOT_FOUND")

    # 2. Validate ward_code if provided
    update_data = payload.model_dump(exclude_unset=True)
    if "ward_code" in update_data and update_data["ward_code"] is not None:
        await _validate_ward_code(db, update_data["ward_code"])

    # 3. Handle is_active idempotency — skip update if same value
    if "is_active" in update_data and update_data["is_active"] == depot.is_active:
        del update_data["is_active"]
    if not update_data and not images:
        # Nothing to update
        return depot

    # 4. Upload new images if provided
    new_keys = await _upload_images(images, "depot") if images else []

    # 5. Merge image_urls: payload image_urls replaces base, new uploads always append
    if "image_urls" in update_data:
        base_urls = list(update_data["image_urls"] or [])
        base_urls.extend(new_keys)
        update_data["image_urls"] = base_urls
    elif new_keys:
        # Keep existing + append new
        base_urls = list(depot.image_urls or [])
        base_urls.extend(new_keys)
        update_data["image_urls"] = base_urls

    # 6. Rebuild payload
    final_payload = DepotUpdate(**update_data)

    # 7. Delegate to CRUD
    return await depot_crud.update_depot(db, depot=depot, payload=final_payload)
