from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from enum import Enum
from datetime import datetime

# --- Enums ---
class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    delivered = "delivered"
    out_for_delivery = "out_for_delivery"
    cancelled = "cancelled"

# --- Seller ---
class BaseSeller(BaseModel):
    name: str
    email: EmailStr

class SellerRead(BaseSeller):
    class Config:
        orm_mode = True

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
        orm_mode = True

# --- Shipment ---
class BaseShipment(BaseModel):
    content: str
    weight: float
    destination: int

class ShipmentCreate(BaseShipment):
    client_email_id: EmailStr 
    client_contact_phone:int  | None = Field(default=None)
    

class ShipmentUpdate(BaseModel):
    location: int | None = Field(default=None)
    description: str | None = Field(default=None)  # ✅ Fixed spelling here
    status: ShipmentStatus | None = None
    estimated_delivery_date: datetime | None = None


class ShipmentRead(BaseShipment):
    id: UUID
    timeline: list[ShipmentEventRead]
    estimated_delivery_date: datetime
    seller: SellerRead

    class Config:
        orm_mode = True

# --- Delivery Partner ---
class BaseDeliveryPartner(BaseModel):
    name: str
    email: EmailStr
    serviceable_zip_codes: list[int]
    max_handling_capacity: int

class DeliveryPartnerRead(BaseDeliveryPartner):
    class Config:
        orm_mode = True

class DeliveryPartnerUpdate(BaseDeliveryPartner):
    serviceable_zip_codes: list[int] | None = Field(default=None)
    max_handling_capacity: int | None = Field(default=None)

class DeliveryPartnerCreate(BaseDeliveryPartner):
    password: str
