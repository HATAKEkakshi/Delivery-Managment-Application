# app/services/shipment.py
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from services.delivery_partner import DeliveryPartnerService
from services.base import BaseService
from database.model import Seller, Shipment
from schemas.schemas import ShipmentCreate, ShipmentRead, ShipmentStatus, ShipmentUpdate
from datetime import datetime, timedelta

class ShipmentService(BaseService):
    def __init__(self, session: AsyncSession,partner_service=DeliveryPartnerService):
        super().__init__(Shipment, session)
        self.partner_service = partner_service

    async def get(self, id: UUID) -> Shipment | None:
        return await self._get( id)

    async def add(self, shipment_create: ShipmentCreate,seller:Seller) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery_date=datetime.now() + timedelta(days=3),
            seller_id=seller.id , # Assuming Shipment model has a seller_id field
        )
        partner=await self.partner_service.assign_shipment(new_shipment)
        new_shipment.id = partner.id
        return await self._add(new_shipment)

    async def update(self, id: int, shipment_update: dict) -> Shipment:
        shipment = await self.session.get(Shipment, id)
        if not shipment:
            raise Exception("Shipment not found")

        for key, value in shipment_update.items():
            setattr(shipment, key, value)

        return await self._update(shipment)
         

    async def delete(self, id: int) -> None:
        await self._delete(await self.get(id))

