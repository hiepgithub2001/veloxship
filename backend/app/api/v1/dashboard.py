"""Dashboard API — aggregated logistics summary."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

_get_db = Depends(get_db)
_require_dashboard_view = Depends(require_permission("dashboard:view"))


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    days: int = Query(30, ge=7, le=90),
    db: AsyncSession = _get_db,
    current_user: User = _require_dashboard_view,
):
    """Return the logistics dashboard summary for the last ``days`` days."""
    return await dashboard_service.get_summary(db, days=days)
