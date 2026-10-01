"""Comment schemas — create, update, and read (with one-level replies)."""

import re
from datetime import datetime
from typing import Literal

import nh3
from pydantic import BaseModel, field_serializer, field_validator

from app.services.storage import extract_key_from_presigned_url, generate_presigned_url

_ENTITY_TYPES = Literal["bill", "customer", "depot", "vehicle"]

# Rich-text whitelist — mirrors the frontend toolbar (TipTap StarterKit).
_ALLOWED_TAGS = {
    "p",
    "br",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "s",
    "strike",
    "ul",
    "ol",
    "li",
    "blockquote",
    "code",
    "pre",
    "h1",
    "h2",
    "h3",
    "a",
    "hr",
    "img",
}

_TAG_RE = re.compile(r"<[^>]+>")
_IMG_SRC_RE = re.compile(r'(<img\b[^>]*?\bsrc=")([^"]*)(")')


def _normalize_img_srcs(html: str) -> str:
    """Convert our own presigned URLs back to object keys so stored bodies never
    contain expiring URLs; external or relative ``src`` values are left as-is."""

    def _repl(match: re.Match) -> str:
        key = extract_key_from_presigned_url(match.group(2))
        if key:
            return f"{match.group(1)}{key}{match.group(3)}"
        return match.group(0)

    return _IMG_SRC_RE.sub(_repl, html)


def _presign_body_images(body: str) -> str:
    """Presign every inline image key when returning a comment body."""

    def _repl(match: re.Match) -> str:
        url = generate_presigned_url(match.group(2))
        return f"{match.group(1)}{url}{match.group(3)}"

    return _IMG_SRC_RE.sub(_repl, body)


def _sanitize_body(value: str) -> str:
    """Strip unsafe HTML from a comment body and validate its content."""
    cleaned = nh3.clean(
        value,
        tags=_ALLOWED_TAGS,
        attributes={"a": {"href", "target"}, "img": {"src", "alt", "title"}},
        url_schemes={"http", "https", "mailto"},
        link_rel="nofollow noopener noreferrer",
    )
    cleaned = _normalize_img_srcs(cleaned)
    text = _TAG_RE.sub("", cleaned).replace("&nbsp;", " ").strip()
    if not text and "<img" not in cleaned:
        raise ValueError("Nội dung bình luận không được để trống")
    if len(text) > 5000:
        raise ValueError("Nội dung bình luận tối đa 5000 ký tự")
    if len(cleaned) > 20000:
        raise ValueError("Nội dung bình luận quá dài")
    return cleaned


class CommentCreate(BaseModel):
    """Schema for creating a root comment or reply."""

    entity_type: _ENTITY_TYPES
    entity_id: int
    body: str
    images: list[str] = []
    parent_id: int | None = None

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: str) -> str:
        return _sanitize_body(v)

    @field_validator("images")
    @classmethod
    def validate_images(cls, v: list[str]) -> list[str]:
        if len(v) > 5:
            raise ValueError("Tối đa 5 hình ảnh cho bình luận")
        return v


class CommentUpdate(BaseModel):
    """Schema for partial comment update."""

    body: str | None = None
    images: list[str] | None = None

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return _sanitize_body(v)

    @field_validator("images")
    @classmethod
    def validate_images(cls, v: list[str] | None) -> list[str] | None:
        if v is not None and len(v) > 5:
            raise ValueError("Tối đa 5 hình ảnh cho bình luận")
        return v


class CommentRead(BaseModel):
    """Schema for comment response, with replies nested (one level)."""

    id: int
    entity_type: str
    entity_id: int
    author_id: int
    author_name: str | None = None
    body: str
    images: list[str] = []
    parent_id: int | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    replies: list["CommentRead"] = []

    @field_serializer("images")
    def serialize_images(self, images: list[str]) -> list[str]:
        if not images:
            return []
        return [generate_presigned_url(img) for img in images]

    @field_serializer("body")
    def serialize_body(self, body: str) -> str:
        return _presign_body_images(body)

    @classmethod
    def from_model(cls, comment) -> "CommentRead":
        """Convert a Comment ORM model to a CommentRead schema."""
        return cls(
            id=comment.id,
            entity_type=comment.entity_type,
            entity_id=comment.entity_id,
            author_id=comment.author_id,
            author_name=comment.author.full_name if comment.author else None,
            body=comment.body,
            images=comment.images or [],
            parent_id=comment.parent_id,
            is_active=comment.is_active,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            replies=[],
        )
