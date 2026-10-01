"""Comment CRUD operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate


async def list_comments(
    db: AsyncSession, *, entity_type: str, entity_id: int
) -> list[Comment]:
    """List active comments for an entity (root + replies), oldest first."""
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author))
        .where(
            Comment.entity_type == entity_type,
            Comment.entity_id == entity_id,
            Comment.is_active.is_(True),
        )
        .order_by(Comment.created_at.asc())
    )
    return list(result.scalars().unique().all())


async def get_comment(db: AsyncSession, comment_id: int) -> Comment | None:
    """Get a single comment (with author) by id."""
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author))
        .where(Comment.id == comment_id)
    )
    return result.scalars().unique().one_or_none()


async def create_comment(db: AsyncSession, *, payload: CommentCreate, author_id: int) -> Comment:
    """Create a new comment record."""
    comment = Comment(
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        author_id=author_id,
        body=payload.body,
        images=payload.images or [],
        parent_id=payload.parent_id,
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    return comment


async def update_comment(db: AsyncSession, *, comment: Comment, payload: CommentUpdate) -> Comment:
    """Partial update — only set fields that are explicitly provided."""
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)
    await db.flush()
    await db.refresh(comment)
    return comment


async def soft_delete_comment(db: AsyncSession, *, comment: Comment) -> None:
    """Soft-delete a comment and its direct replies (one level)."""
    comment.is_active = False
    result = await db.execute(select(Comment).where(Comment.parent_id == comment.id))
    for reply in result.scalars():
        reply.is_active = False
    await db.flush()
