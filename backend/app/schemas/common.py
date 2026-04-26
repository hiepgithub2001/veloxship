"""Common schemas — error response and pagination primitives."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Standard error body returned by all error handlers."""
    error_code: str
    message: str
    details: dict | None = None


class Page(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: list[T]
    page: int
    page_size: int
    total: int
