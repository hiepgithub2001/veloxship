"""Comment business logic — polymorphic attach, one-level replies, ownership."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, ConflictError, ForbiddenError, NotFoundError
from app.crud import comment as comment_crud
from app.models.bill import Bill
from app.models.comment import Comment
from app.models.customer import Customer
from app.models.depot import Depot
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.comment import CommentCreate, CommentRead, CommentUpdate

_ENTITY_MODELS = {
    "bill": Bill,
    "customer": Customer,
    "depot": Depot,
    "vehicle": Vehicle,
}


async def _validate_entity(db: AsyncSession, entity_type: str, entity_id: int) -> None:
    """Raise AppError if entity_type is unknown or the entity doesn't exist."""
    model = _ENTITY_MODELS.get(entity_type)
    if model is None:
        raise AppError("COMMENT_ENTITY_INVALID", status_code=422)
    result = await db.execute(select(model.id).where(model.id == entity_id))
    if result.scalar_one_or_none() is None:
        raise NotFoundError("COMMENT_ENTITY_NOT_FOUND")


def _assert_can_modify(comment: Comment, current_user: User) -> None:
    """Raise ForbiddenError unless the user authored the comment or is admin."""
    if comment.author_id != current_user.id and current_user.role != "admin":
        raise ForbiddenError("COMMENT_FORBIDDEN")


def _build_thread(comments: list[Comment]) -> list[CommentRead]:
    """Group a flat comment list into root comments with inline replies (one level)."""
    read_map = {c.id: CommentRead.from_model(c) for c in comments}
    roots: list[CommentRead] = []
    for c in comments:
        node = read_map[c.id]
        if c.parent_id is not None and c.parent_id in read_map:
            read_map[c.parent_id].replies.append(node)
        else:
            roots.append(node)
    return roots


async def list_comments(db: AsyncSession, entity_type: str, entity_id: int) -> list[CommentRead]:
    """List comments for an entity, threaded (root + inline replies)."""
    await _validate_entity(db, entity_type, entity_id)
    comments = await comment_crud.list_comments(db, entity_type=entity_type, entity_id=entity_id)
    return _build_thread(comments)


async def create_comment(db: AsyncSession, payload: CommentCreate, current_user: User) -> Comment:
    """Create a root comment or reply after validating the entity and parent."""
    await _validate_entity(db, payload.entity_type, payload.entity_id)

    if payload.parent_id is not None:
        parent = await comment_crud.get_comment(db, payload.parent_id)
        if parent is None or not parent.is_active:
            raise NotFoundError("COMMENT_PARENT_INVALID")
        if parent.entity_type != payload.entity_type or parent.entity_id != payload.entity_id:
            raise ConflictError("COMMENT_PARENT_INVALID")
        if parent.parent_id is not None:
            raise ConflictError("COMMENT_PARENT_INVALID")

    comment = await comment_crud.create_comment(
        db, payload=payload, author_id=current_user.id
    )
    # Attach the already-loaded author so create response includes author_name.
    comment.author = current_user
    return comment


async def update_comment(
    db: AsyncSession, comment_id: int, payload: CommentUpdate, current_user: User
) -> Comment:
    """Update a comment (author or admin only)."""
    comment = await comment_crud.get_comment(db, comment_id)
    if comment is None or not comment.is_active:
        raise NotFoundError("COMMENT_NOT_FOUND")
    _assert_can_modify(comment, current_user)
    return await comment_crud.update_comment(db, comment=comment, payload=payload)


async def delete_comment(db: AsyncSession, comment_id: int, current_user: User) -> None:
    """Soft-delete a comment and its replies (author or admin only)."""
    comment = await comment_crud.get_comment(db, comment_id)
    if comment is None or not comment.is_active:
        raise NotFoundError("COMMENT_NOT_FOUND")
    _assert_can_modify(comment, current_user)
    await comment_crud.soft_delete_comment(db, comment=comment)
