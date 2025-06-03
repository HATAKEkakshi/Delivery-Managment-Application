from sqlmodel import SQLModel,Field
from app.schemas import ShipmentStatus
from datetime import datetime
class Shipment(SQLModel,table=True):
    __tablename__="shipment"
    id :int=Field(default=None,primary_key=True)
    content:str
    weight:float=Field(le=25)
    destination:int
    status:ShipmentStatus
    estimated_delivery_date:datetime 