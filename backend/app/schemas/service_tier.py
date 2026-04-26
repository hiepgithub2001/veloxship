"""Service tier schema."""

from pydantic import BaseModel


class ServiceTierRead(BaseModel):
    """Service tier response."""
    code: str
    display_name: str
    scope: str
    is_active: bool

    model_config = {"from_attributes": True}
