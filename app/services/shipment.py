# app/services/shipment.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from database.model import Shipment
from app.schemas import ShipmentCreate, ShipmentRead, ShipmentStatus, ShipmentUpdate
from datetime import datetime, timedelta

class ShipmentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Shipment | None:
        return await self.session.get(Shipment, id)

    async def add(self, shipment_create: ShipmentCreate) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery_date=datetime.now() + timedelta(days=3)
        )
        self.session.add(new_shipment)
        await self.session.commit()
        await self.session.refresh(new_shipment)
        return new_shipment

    async def update(self, id: int, shipment_update: dict) -> Shipment:
        shipment = await self.session.get(Shipment, id)
        if not shipment:
            raise Exception("Shipment not found")

        for key, value in shipment_update.items():
            setattr(shipment, key, value)

        self.session.add(shipment)
        await self.session.commit()
        await self.session.refresh(shipment)
        return shipment

    async def delete(self, id: int) -> None:
        shipment = await self.session.get(Shipment, id)
        if not shipment:
            raise Exception("Shipment not found")
        await self.session.delete(shipment)
        await self.session.commit()
