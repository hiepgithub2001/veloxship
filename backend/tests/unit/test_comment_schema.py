"""Unit tests for comment body HTML sanitization (XSS protection) and inline images."""

from datetime import datetime
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.schemas.comment import CommentCreate, CommentRead, CommentUpdate


class TestSanitizeBody:
    def test_plain_text_passes_through(self):
        payload = CommentCreate(entity_type="depot", entity_id=1, body="Bình luận")
        assert payload.body == "Bình luận"

    def test_script_tags_are_stripped(self):
        payload = CommentCreate(
            entity_type="depot",
            entity_id=1,
            body="<p>Xin chào</p><script>alert(1)</script>",
        )
        assert "<script" not in payload.body
        assert "Xin chào" in payload.body

    def test_unsafe_link_attributes_are_stripped(self):
        payload = CommentCreate(
            entity_type="depot",
            entity_id=1,
            body='<a href="https://example.com" onclick="alert(1)">link</a>',
        )
        assert 'href="https://example.com"' in payload.body
        assert "onclick" not in payload.body
        assert 'rel="nofollow noopener noreferrer"' in payload.body

    def test_empty_html_is_rejected(self):
        with pytest.raises(ValidationError):
            CommentCreate(entity_type="depot", entity_id=1, body="<p></p>")

    def test_update_sanitizes_too(self):
        payload = CommentUpdate(body="<b>đậm</b><img src=x onerror=alert(1)>")
        assert "onerror" not in payload.body
        assert "<b>đậm</b>" in payload.body


class TestInlineImages:
    def test_image_key_src_is_preserved(self):
        payload = CommentCreate(
            entity_type="depot",
            entity_id=1,
            body='<p><img src="uploads/a.jpg"></p>',
        )
        assert 'src="uploads/a.jpg"' in payload.body

    def test_image_event_handler_is_stripped(self):
        payload = CommentCreate(
            entity_type="depot",
            entity_id=1,
            body='<img src="uploads/a.jpg" onerror="alert(1)">',
        )
        assert "onerror" not in payload.body
        assert 'src="uploads/a.jpg"' in payload.body

    def test_image_javascript_src_is_stripped(self):
        payload = CommentCreate(
            entity_type="depot",
            entity_id=1,
            body='<img src="javascript:alert(1)">',
        )
        assert "javascript:" not in payload.body

    def test_image_only_comment_is_allowed(self):
        payload = CommentCreate(
            entity_type="depot",
            entity_id=1,
            body='<p><img src="uploads/a.jpg"></p>',
        )
        assert payload.body  # no ValidationError

    def test_body_images_are_presigned_on_serialization(self):
        with patch(
            "app.schemas.comment.generate_presigned_url",
            side_effect=lambda key: f"https://cdn/{key}",
        ):
            comment = CommentRead(
                id=1,
                entity_type="depot",
                entity_id=1,
                author_id=1,
                body='<p>Ảnh: <img src="uploads/a.jpg"></p>',
                is_active=True,
                created_at=datetime(2026, 1, 1),
                updated_at=datetime(2026, 1, 1),
            )
            dumped = comment.model_dump(mode="json")
        assert 'src="https://cdn/uploads/a.jpg"' in dumped["body"]
