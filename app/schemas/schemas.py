# app/schemas/schemas.py
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

# Import enums from models to avoid circular imports
from app.database.model import ShipmentStatus, TagName

# --- Tag ---
class TagRead(BaseModel):
    name: str
    instruction: str

    class Config:
        from_attributes = True

# --- Seller ---
class BaseSeller(BaseModel):
    name: str
    email: EmailStr

class SellerRead(BaseSeller):
    class Config:
        from_attributes = True

class SellerCreate(BaseSeller):
    password: str

# --- ShipmentEvent ---
class ShipmentEventRead(BaseModel):
    id: UUID
    location: int
    status: ShipmentStatus
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Shipment ---
class BaseShipment(BaseModel):
    content: str
    weight: float
    destination: int

class ShipmentCreate(BaseShipment):
    client_email_id: EmailStr 
    client_contact_phone: str | None = Field(default=None)

class ShipmentUpdate(BaseModel):
    location: int | None = Field(default=None)
    description: str | None = Field(default=None)
    status: ShipmentStatus | None = None
    estimated_delivery_date: datetime | None = None
    verification_code: str | None = Field(default=None)

class ShipmentRead(BaseShipment):
    id: UUID
    timeline: list[ShipmentEventRead]
    estimated_delivery_date: datetime
    seller: SellerRead
    tags: list[TagRead]

    class Config:
        from_attributes = True

class ShipmentReview(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None)

# --- Delivery Partner ---
class BaseDeliveryPartner(BaseModel):
    name: str
    email: EmailStr
    serviceable_zip_codes: list[int]
    max_handling_capacity: int

class DeliveryPartnerRead(BaseDeliveryPartner):
    class Config:
        from_attributes = True

class DeliveryPartnerUpdate(BaseModel):
    serviceable_zip_codes: list[int] | None = Field(default=None)
    max_handling_capacity: int | None = Field(default=None)

class DeliveryPartnerCreate(BaseDeliveryPartner):
    password: str