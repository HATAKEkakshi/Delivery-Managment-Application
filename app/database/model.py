from sqlalchemy import Column
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
    estimated_delivery_date:datetime 
    seller_id:UUID =Field(foreign_key="seller.id")
    seller:"Seller"=Relationship(back_populates="shipments",sa_relationship_kwargs={"lazy": "selectin"})
class Seller(SQLModel,table=True):
    id :UUID=Field(sa_column=Column(postgresql.UUID,default=uuid4, primary_key=True))
    name:str
    email:EmailStr
    password_hash:str
    shipments:list[Shipment] = Relationship(back_populates="seller",sa_relationship_kwargs={"lazy": "selectin"})