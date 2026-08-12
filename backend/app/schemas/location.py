"""Location schemas — provinces and wards."""

from pydantic import BaseModel


class ProvinceRead(BaseModel):
    """Province response schema."""

    code: str
    name: str
    name_en: str | None = None

    model_config = {"from_attributes": True}


class WardRead(BaseModel):
    """Ward response schema."""

    code: str
    name: str
    name_en: str | None = None
    province_code: str

    model_config = {"from_attributes": True}
