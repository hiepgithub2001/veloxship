"""Dashboard API — aggregated logistics summary."""

from datetime import date

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
_date_from_query = Query(None, description="Ngày bắt đầu (YYYY-MM-DD).")
_date_to_query = Query(None, description="Ngày kết thúc (YYYY-MM-DD).")


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    date_from: date | None = _date_from_query,
    date_to: date | None = _date_to_query,
    db: AsyncSession = _get_db,
    current_user: User = _require_dashboard_view,
):
    """Return the logistics dashboard summary for the given date range.

    Both bounds are optional; when omitted the last 30 VN days are used.
    """
    return await dashboard_service.get_summary(db, date_from=date_from, date_to=date_to)
