"""Locations API — provinces and wards endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import location as location_crud
from app.db.session import get_db
from app.schemas.location import ProvinceRead, WardRead

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/provinces", response_model=list[ProvinceRead])
async def list_provinces(db: AsyncSession = Depends(get_db)):
    """Return all provinces."""
    provinces = await location_crud.list_provinces(db)
    return [ProvinceRead.model_validate(p) for p in provinces]


@router.get("/provinces/{province_code}/wards", response_model=list[WardRead])
async def list_wards_by_province(
    province_code: str,
    db: AsyncSession = Depends(get_db),
):
    """Return all wards belonging to a given province."""
    wards = await location_crud.list_wards_by_province(db, province_code)
    if not wards:
        # Check if the province exists at all
        from app.models.province import Province
        from sqlalchemy import select

        result = await db.execute(
            select(Province).where(Province.code == province_code)
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Province with code '{province_code}' not found.",
            )
    return [WardRead.model_validate(w) for w in wards]
