from typing import Any
from pydantic import BaseModel, Field
from random import randint
from enum import Enum
from datetime import datetime
def random_destination() -> int:
    return randint(11000, 11999)

class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    delivered = "delivered"
    out_for_delivery = "out_for_delivery"

class BaseShipment(BaseModel):
    content: str = Field(..., max_length=30)
    weight: float = Field(..., le=25, ge=1)
    destination: int = Field(default_factory=random_destination)

class ShipmentCreate(BaseShipment):
    pass

class ShipmentRead(BaseShipment):
    status: ShipmentStatus
    # Optional: Include `id` in read schema if you want to expose it in responses
    id: int
    estimated_delivery_date: datetime
class ShipmentUpdate(BaseModel):
    status: ShipmentStatus | None =Field(default=None)
    estimated_delivery_date: datetime| None =Field(default=None)

