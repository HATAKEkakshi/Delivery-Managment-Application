from sqlalchemy import Column,ARRAY,INTEGER
from sqlmodel import SQLModel,Field,Relationship
from sqlalchemy.dialects import postgresql
from schemas.schemas import ShipmentStatus
from datetime import datetime
from pydantic import EmailStr
from uuid import uuid4,UUID
# In service.py
    # use Seller here

class Shipment(SQLModel,table=True):
    __tablename__="shipment"
    id :UUID=Field(sa_column=Column(postgresql.UUID,default=uuid4, primary_key=True))
    content:str
    weight:float=Field(le=25)
    destination:int
    status:ShipmentStatus
    created_at:datetime = Field(sa_column=Column(postgresql.TIMESTAMP,default=datetime.now))
    estimated_delivery_date:datetime 
    seller_id:UUID =Field(foreign_key="seller.id")
    seller:"Seller"=Relationship(back_populates="shipments",sa_relationship_kwargs={"lazy": "selectin"})
    delivery_partner_id:UUID = Field(foreign_key="delivery_partner.id")
    delivery_partner:"DeliveryPartner"=Relationship(back_populates="shipments",sa_relationship_kwargs={"lazy": "selectin"})
class User(SQLModel):
    name: str
    email: EmailStr  # ✅ Fix is here
    password_hash: str = Field(exclude=True)
class Seller(User,table=True):
    __tablename__="seller"
    id :UUID=Field(sa_column=Column(postgresql.UUID,default=uuid4, primary_key=True))
    created_at:datetime = Field(sa_column=Column(postgresql.TIMESTAMP,default=datetime.now))
    shipments:list[Shipment] = Relationship(back_populates="seller",sa_relationship_kwargs={"lazy": "selectin"})
class DeliveryPartner(User,table=True):
    __tablename__="delivery_partner"
    email: str | None = Field(default=None)
    id :UUID=Field(sa_column=Column(postgresql.UUID,default=uuid4, primary_key=True))
    created_at:datetime = Field(sa_column=Column(postgresql.TIMESTAMP,default=datetime.now))
    serviceable_zip_codes:list[int] = Field(sa_column=Column(ARRAY(INTEGER)))
    max_handling_capacity:int
    shipments:list[Shipment] = Relationship(back_populates="delivery_partner",sa_relationship_kwargs={"lazy": "selectin"})
    @property
    def active_shipments(self):
        return [
            shipment
            for shipment in self.shipments
            if shipment.status != ShipmentStatus.delivered  # Fix this too (was filtering only 'delivered')
        ]

    @property
    def current_handling_capacity(self):
        return self.max_handling_capacity - len(self.active_shipments)