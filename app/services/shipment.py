from uuid import UUID
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from services.shipmentevent import ShipmentEventService
from services.delivery_partner import DeliveryPartnerService
from services.base import BaseService
from database.model import DeliveryPartner, Seller, Shipment
from schemas.schemas import ShipmentCreate, ShipmentRead, ShipmentStatus, ShipmentUpdate
from datetime import datetime, timedelta
from database.redis import get_shipment_verification_code

class ShipmentService(BaseService):
    def __init__(self, session: AsyncSession, partner_service: DeliveryPartnerService, event_service: ShipmentEventService):
        super().__init__(Shipment, session)
        self.partner_service = partner_service
        self.event_service = event_service

    async def get(self, id: UUID) -> Shipment | None:
        return await self._get(id)

    async def add(self, shipment_create: ShipmentCreate, seller: Seller) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            estimated_delivery_date=datetime.now() + timedelta(days=3),
            seller_id=seller.id,
            status=ShipmentStatus.placed,
        )

        # Assign delivery partner based on shipment destination
        partner = await self.partner_service.assign_shipment(new_shipment)
        new_shipment.delivery_partner_id = partner.id

        shipment = await self._add(new_shipment)

        # Add shipment event
        await self.event_service.add(
            shipment=shipment,
            location=seller.zipcode,
            status=ShipmentStatus.placed,
            description=f"Assigned to {partner.name}."
        )
        # No need to append or refresh timeline manually
        return shipment

    async def update(
        self,
        id: UUID,
        shipment_update: ShipmentUpdate,
        partner: DeliveryPartner,
        partner_service: DeliveryPartnerService
    ):
        shipment = await self._get(id)
        if shipment is None:
            raise HTTPException(status_code=404, detail="Shipment not found")

        if shipment.delivery_partner_id != partner.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this shipment")
        if shipment_update.status == ShipmentStatus.delivered:
            code= await get_shipment_verification_code(shipment.id)
            if code!=shipment_update.verification_code:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Client not authorized"
                    )
        # Apply update
        for key, value in shipment_update.model_dump(exclude_unset=True,exclude=["verification_code"]).items():
            if hasattr(shipment, key):
                setattr(shipment, key, value)

        # Optional: log event (status/location/description)
        if shipment_update.status or shipment_update.location or shipment_update.description:
            await self.event_service.add(
            shipment=shipment,
            location=shipment_update.location,
            status=shipment_update.status or shipment.status,
            description=shipment_update.description
        )

        return await self._update(shipment)



    async def cancel(self, id: UUID, seller: Seller):
        shipment = await self.get(id)
        if shipment.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to cancel this shipment."
            )
        event= await self.event_service.add(
            shipment=shipment,
            status=ShipmentStatus.cancelled,
            description="Shipment cancelled by seller."
        )
        shipment.timeline.append(event)
        return shipment
        # No need to refresh or append manually

    async def delete(self, id: int) -> None:
        await self._delete(await self.get(id))
