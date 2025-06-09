from pydantic import BaseModel, EmailStr
from uuid import UUID
from enum import Enum
from datetime import datetime

class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    delivered = "delivered"
    out_for_delivery = "out_for_delivery"

# Base Schemas
class BaseSeller(BaseModel):
    name: str
    email: EmailStr

class SellerRead(BaseSeller):
    pass

class SellerCreate(BaseSeller):
    password: str

class BaseShipment(BaseModel):
    content: str
    weight: float
    destination: int

class ShipmentCreate(BaseShipment):
    pass

class ShipmentUpdate(BaseModel):
    status: ShipmentStatus | None = None
    estimated_delivery_date: datetime | None = None

class ShipmentRead(BaseShipment):
    id: UUID
    status: ShipmentStatus
    estimated_delivery_date: datetime
    seller: "SellerRead"  # Forward reference to SellerRead

