"""Bill schemas — create, read, status, events."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, field_validator


class BillStatus(str, Enum):
    da_tao = "da_tao"
    da_lay_hang = "da_lay_hang"
    dang_van_chuyen = "dang_van_chuyen"
    da_giao = "da_giao"
    hoan_tra = "hoan_tra"
    huy = "huy"


class Party(BaseModel):
    """Sender or receiver block."""
    name: str
    address: str
    district: str
    province: str
    phone: str


class BillContentLineSchema(BaseModel):
    """A single content line in the bill."""
    line_no: int | None = None
    description: str
    quantity: int
    weight_kg: float
    length_cm: float | None = None
    width_cm: float | None = None
    height_cm: float | None = None

    model_config = {"from_attributes": True}


class FeeBreakdown(BaseModel):
    """Fee breakdown with total validation."""
    fee_main: float
    fee_fuel_surcharge: float
    fee_other_surcharge: float
    fee_vat: float
    fee_total: float

    @field_validator("fee_total")
    @classmethod
    def validate_total(cls, v, info):
        data = info.data
        expected = (
            data.get("fee_main", 0)
            + data.get("fee_fuel_surcharge", 0)
            + data.get("fee_other_surcharge", 0)
            + data.get("fee_vat", 0)
        )
        if abs(v - expected) > 0.01:
            raise ValueError("Tổng cước không khớp với tổng các khoản.")
        return v


class BillCreate(BaseModel):
    """POST /bills request body."""
    customer_id: int | None = None
    customer_code: str | None = None
    sender: Party
    receiver: Party
    contents: list[BillContentLineSchema]
    cargo_type: str
    service_tier_code: str
    fee: FeeBreakdown
    payer: str


class BillStatusUpdate(BaseModel):
    """POST /bills/{id}/status request body."""
    to_status: BillStatus
    delivered_to_name: str | None = None
    cancellation_reason: str | None = None
    note: str | None = None


class BillStatusEventRead(BaseModel):
    """Status event in the response."""
    id: int
    bill_id: int
    from_status: str | None = None
    to_status: str
    note: str | None = None
    actor_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class BillRead(BaseModel):
    """Full bill response."""
    id: int
    tracking_number: str
    customer_code: str | None = None
    customer_id: int | None = None
    sender: Party
    receiver: Party
    contents: list[BillContentLineSchema]
    cargo_type: str
    service_tier_code: str
    fee: FeeBreakdown
    payer: str
    status: str
    delivered_at: datetime | None = None
    delivered_to_name: str | None = None
    cancellation_reason: str | None = None
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    print_count: int
    last_printed_at: datetime | None = None
    last_printed_by: int | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, bill):
        """Convert a Bill ORM model to a BillRead schema."""
        return cls(
            id=bill.id,
            tracking_number=bill.tracking_number,
            customer_code=bill.customer_code,
            customer_id=bill.customer_id,
            sender=Party(
                name=bill.sender_name,
                address=bill.sender_address,
                district=bill.sender_district,
                province=bill.sender_province,
                phone=bill.sender_phone,
            ),
            receiver=Party(
                name=bill.receiver_name,
                address=bill.receiver_address,
                district=bill.receiver_district,
                province=bill.receiver_province,
                phone=bill.receiver_phone,
            ),
            contents=[BillContentLineSchema.model_validate(line) for line in bill.content_lines],
            cargo_type=bill.cargo_type,
            service_tier_code=bill.service_tier_code,
            fee=FeeBreakdown(
                fee_main=float(bill.fee_main),
                fee_fuel_surcharge=float(bill.fee_fuel_surcharge),
                fee_other_surcharge=float(bill.fee_other_surcharge),
                fee_vat=float(bill.fee_vat),
                fee_total=float(bill.fee_total),
            ),
            payer=bill.payer,
            status=bill.status,
            delivered_at=bill.delivered_at,
            delivered_to_name=bill.delivered_to_name,
            cancellation_reason=bill.cancellation_reason,
            created_at=bill.created_at,
            updated_at=bill.updated_at,
            created_by=bill.created_by,
            updated_by=bill.updated_by,
            print_count=bill.print_count,
            last_printed_at=bill.last_printed_at,
            last_printed_by=bill.last_printed_by,
        )


class BillPage(BaseModel):
    """Paginated bill list response."""
    items: list[BillRead]
    page: int
    page_size: int
    total: int
