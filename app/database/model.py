# app/database/model.py
from sqlalchemy import Column, INTEGER, select, JSON, Text
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.dialects import postgresql
from datetime import datetime
from pydantic import EmailStr
from uuid import uuid4, UUID
from enum import Enum
import json

# Move enums to models since they're used by database models
class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    delivered = "delivered"
    out_for_delivery = "out_for_delivery"
    cancelled = "cancelled"

class TagName(str, Enum):
    EXPRESS = "express"
    STANDARD = "standard"
    FRAGILE = "fragile"
    HEAVY = "heavy"
    INTERNATIONAL = "international"
    DOMESTIC = "domestic"
    TEMPERATURE_CONTROLLED = "temperature_controlled"
    GIFT = "gift"
    RETURN = "return"
    DOCUMENTS = "documents"
    
    async def tag(self, session):
        # No circular import since we're in the same file
        return await session.scalar(
            select(Tag).where(Tag.name == self.value)
        )

class User(SQLModel):
    name: str
    email: EmailStr
    email_verified: bool = Field(default=False)
    password_hash: str

class ShipmentTag(SQLModel, table=True):
    __tablename__ = "shipment_tag"
    shipment_id: UUID = Field(foreign_key="shipment.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tag.id", primary_key=True)

class Seller(User, table=True):
    __tablename__ = "seller"
    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))
    created_at: datetime = Field(sa_column=Column(postgresql.TIMESTAMP, default=datetime.now))
    address: str | None = Field(default=None)
    zipcode: int | None = Field(default=None)
    shipments: list["Shipment"] = Relationship(back_populates="seller", sa_relationship_kwargs={"lazy": "selectin"})

class DeliveryPartner(User, table=True):
    __tablename__ = "delivery_partner"
    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))
    created_at: datetime = Field(sa_column=Column(postgresql.TIMESTAMP, default=datetime.now))
    serviceable_zip_codes: list[int] = Field(sa_column=Column(JSON))
    max_handling_capacity: int
    shipments: list["Shipment"] = Relationship(back_populates="delivery_partner", sa_relationship_kwargs={"lazy": "selectin"})

    @property
    def active_shipments(self):
        return [
            shipment
            for shipment in self.shipments
            if shipment.status != ShipmentStatus.delivered
            or shipment.status != ShipmentStatus.cancelled
        ]

    @property
    def current_handling_capacity(self):
        return self.max_handling_capacity - len(self.active_shipments)

class Tag(SQLModel, table=True):
    __tablename__ = "tag"
    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))
    name: str  # Should store TagName values
    instruction: str
    shipments: list["Shipment"] = Relationship(
        back_populates="tags", link_model=ShipmentTag, sa_relationship_kwargs={"lazy": "immediate"}
    )

class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"
    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))
    content: str
    weight: float = Field(le=25)
    destination: int
    status: ShipmentStatus
    created_at: datetime = Field(sa_column=Column(postgresql.TIMESTAMP, default=datetime.now))

    client_email_id: EmailStr | None
    client_contact_phone: str | None
    estimated_delivery_date: datetime

    timeline: list["ShipmentEvent"] = Relationship(
        back_populates="shipment", sa_relationship_kwargs={"lazy": "selectin"}
    )

    seller_id: UUID = Field(foreign_key="seller.id")
    seller: Seller = Relationship(back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"})

    delivery_partner_id: UUID = Field(foreign_key="delivery_partner.id")
    delivery_partner: DeliveryPartner = Relationship(back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"})

    review: "Review" = Relationship(back_populates="shipment", sa_relationship_kwargs={"lazy": "selectin"})

    tags: list["Tag"] = Relationship(
        back_populates="shipments", link_model=ShipmentTag, sa_relationship_kwargs={"lazy": "immediate"}
    )

class ShipmentEvent(SQLModel, table=True):
    __tablename__ = "shipment_event"
    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))
    location: int
    status: ShipmentStatus
    description: str | None = Field(default=None)
    created_at: datetime = Field(sa_column=Column(postgresql.TIMESTAMP, default=datetime.now))

    shipment_id: UUID = Field(foreign_key="shipment.id")
    shipment: Shipment = Relationship(back_populates="timeline", sa_relationship_kwargs={"lazy": "selectin"})

class Review(SQLModel, table=True):
    __tablename__ = "review"
    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))
    created_at: datetime = Field(sa_column=Column(postgresql.TIMESTAMP, default=datetime.now))
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None)

    shipment_id: UUID = Field(foreign_key="shipment.id")
    shipment: Shipment = Relationship(back_populates="review", sa_relationship_kwargs={"lazy": "selectin"})