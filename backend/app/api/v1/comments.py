"""Comments API — polymorphic comment thread endpoints."""

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from app.services import comment_service

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("", response_model=list[CommentRead])
async def list_comments(
    entity_type: str = Query(..., min_length=1, max_length=20),
    entity_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bill:view")),
):
    """List comments for an entity, threaded (root + inline replies)."""
    return await comment_service.list_comments(db, entity_type, entity_id)


@router.post("", response_model=CommentRead, status_code=201)
async def create_comment(
    body: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bill:update")),
):
    """Create a root comment or reply."""
    comment = await comment_service.create_comment(db, body, current_user)
    return CommentRead.from_model(comment)


@router.patch("/{comment_id}", response_model=CommentRead)
async def update_comment(
    comment_id: int,
    body: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bill:update")),
):
    """Update a comment's body/images (author or admin)."""
    comment = await comment_service.update_comment(db, comment_id, body, current_user)
    return CommentRead.from_model(comment)


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bill:update")),
):
    """Soft-delete a comment and its replies (author or admin)."""
    await comment_service.delete_comment(db, comment_id, current_user)
    return Response(status_code=204)
