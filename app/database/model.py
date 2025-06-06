from sqlmodel import SQLModel,Field
from app.schemas.schemas import ShipmentStatus
from datetime import datetime
from pydantic import EmailStr
class Shipment(SQLModel,table=True):
    __tablename__="shipment"
    id :int=Field(default=None,primary_key=True)
    content:str
    weight:float=Field(le=25)
    destination:int
    status:ShipmentStatus
    estimated_delivery_date:datetime 
class Seller(SQLModel,table=True):
    id: int = Field(default=None, primary_key=True)
    name:str
    email:EmailStr
    password_hash:str