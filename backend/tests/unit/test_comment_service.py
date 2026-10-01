"""Unit tests for app.services.comment_service — create, update, delete flows."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.schemas.comment import CommentCreate, CommentUpdate
from app.services.comment_service import (
    create_comment,
    delete_comment,
    list_comments,
    update_comment,
)


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _make_comment(**overrides):
    """Build a fake Comment object with sensible defaults."""
    defaults = {
        "id": 1,
        "entity_type": "depot",
        "entity_id": 10,
        "author_id": 1,
        "body": "Bình luận",
        "images": [],
        "parent_id": None,
        "is_active": True,
        "created_at": datetime(2026, 10, 1, 10, 0, 0),
        "updated_at": datetime(2026, 10, 1, 10, 0, 0),
        "author": None,
    }
    defaults.update(overrides)
    comment = MagicMock()
    for k, v in defaults.items():
        setattr(comment, k, v)
    return comment


def _make_user(user_id: int = 1, role: str = "operator"):
    """Build a fake current user."""
    user = MagicMock()
    user.id = user_id
    user.role = role
    return user


def _mock_db_execute_result(scalar_value):
    """Create an AsyncMock that mimics db.execute() returning a result with scalar_one_or_none."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_value
    return result


# ─── list_comments tests ────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestListComments:
    @patch("app.services.comment_service.comment_crud")
    async def test_builds_thread(self, mock_crud):
        """Root comments have replies nested inline."""
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_mock_db_execute_result(1))

        root = _make_comment(id=1, parent_id=None)
        reply = _make_comment(id=2, parent_id=1)
        mock_crud.list_comments = AsyncMock(return_value=[root, reply])

        result = await list_comments(db, "depot", 10)

        assert len(result) == 1
        assert result[0].id == 1
        assert len(result[0].replies) == 1
        assert result[0].replies[0].id == 2


# ─── create_comment tests ───────────────────────────────────────────────────


@pytest.mark.asyncio
class TestCreateComment:
    @patch("app.services.comment_service.comment_crud")
    async def test_entity_not_found_raises_not_found_error(self, mock_crud):
        """NotFoundError when the attached entity doesn't exist."""
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_mock_db_execute_result(None))

        payload = CommentCreate(entity_type="depot", entity_id=999, body="hi")

        with pytest.raises(NotFoundError) as exc_info:
            await create_comment(db, payload, _make_user())

        assert exc_info.value.error_code == "COMMENT_ENTITY_NOT_FOUND"

    @patch("app.services.comment_service.comment_crud")
    async def test_reply_to_reply_raises_conflict_error(self, mock_crud):
        """Replying to a reply (depth > 1) raises ConflictError."""
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_mock_db_execute_result(1))

        parent = _make_comment(id=2, parent_id=1)  # already a reply
        mock_crud.get_comment = AsyncMock(return_value=parent)

        payload = CommentCreate(entity_type="depot", entity_id=10, body="hi", parent_id=2)

        with pytest.raises(ConflictError) as exc_info:
            await create_comment(db, payload, _make_user())

        assert exc_info.value.error_code == "COMMENT_PARENT_INVALID"

    @patch("app.services.comment_service.comment_crud")
    async def test_reply_parent_missing_raises_not_found_error(self, mock_crud):
        """Replying to a missing parent raises NotFoundError."""
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_mock_db_execute_result(1))
        mock_crud.get_comment = AsyncMock(return_value=None)

        payload = CommentCreate(entity_type="depot", entity_id=10, body="hi", parent_id=999)

        with pytest.raises(NotFoundError) as exc_info:
            await create_comment(db, payload, _make_user())

        assert exc_info.value.error_code == "COMMENT_PARENT_INVALID"

    @patch("app.services.comment_service.comment_crud")
    async def test_successful_create(self, mock_crud):
        """Successful create delegates to CRUD and returns the comment."""
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_mock_db_execute_result(1))

        created = _make_comment()
        mock_crud.create_comment = AsyncMock(return_value=created)

        payload = CommentCreate(entity_type="depot", entity_id=10, body="hi")
        result = await create_comment(db, payload, _make_user())

        assert result == created
        mock_crud.create_comment.assert_called_once()


# ─── update_comment tests ───────────────────────────────────────────────────


@pytest.mark.asyncio
class TestUpdateComment:
    @patch("app.services.comment_service.comment_crud")
    async def test_not_found_raises_not_found_error(self, mock_crud):
        """NotFoundError when the comment doesn't exist."""
        db = AsyncMock()
        mock_crud.get_comment = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError) as exc_info:
            await update_comment(db, 999, CommentUpdate(body="x"), _make_user())

        assert exc_info.value.error_code == "COMMENT_NOT_FOUND"

    @patch("app.services.comment_service.comment_crud")
    async def test_non_author_raises_forbidden(self, mock_crud):
        """ForbiddenError when a non-author, non-admin tries to update."""
        db = AsyncMock()
        comment = _make_comment(author_id=1)
        mock_crud.get_comment = AsyncMock(return_value=comment)

        with pytest.raises(ForbiddenError) as exc_info:
            await update_comment(db, 1, CommentUpdate(body="x"), _make_user(user_id=2))

        assert exc_info.value.error_code == "COMMENT_FORBIDDEN"

    @patch("app.services.comment_service.comment_crud")
    async def test_admin_can_update_others_comment(self, mock_crud):
        """Admin can update a comment authored by another user."""
        db = AsyncMock()
        comment = _make_comment(author_id=1)
        mock_crud.get_comment = AsyncMock(return_value=comment)
        updated = _make_comment(author_id=1, body="x")
        mock_crud.update_comment = AsyncMock(return_value=updated)

        result = await update_comment(db, 1, CommentUpdate(body="x"), _make_user(role="admin"))

        assert result == updated


# ─── delete_comment tests ───────────────────────────────────────────────────


@pytest.mark.asyncio
class TestDeleteComment:
    @patch("app.services.comment_service.comment_crud")
    async def test_non_author_raises_forbidden(self, mock_crud):
        """ForbiddenError when a non-author, non-admin tries to delete."""
        db = AsyncMock()
        comment = _make_comment(author_id=1)
        mock_crud.get_comment = AsyncMock(return_value=comment)

        with pytest.raises(ForbiddenError) as exc_info:
            await delete_comment(db, 1, _make_user(user_id=2))

        assert exc_info.value.error_code == "COMMENT_FORBIDDEN"

    @patch("app.services.comment_service.comment_crud")
    async def test_author_can_delete(self, mock_crud):
        """Author can delete their own comment."""
        db = AsyncMock()
        comment = _make_comment(author_id=1)
        mock_crud.get_comment = AsyncMock(return_value=comment)
        mock_crud.soft_delete_comment = AsyncMock()

        await delete_comment(db, 1, _make_user(user_id=1))

        mock_crud.soft_delete_comment.assert_called_once_with(db, comment=comment)
