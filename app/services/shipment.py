# app/services/shipment.py
from uuid import UUID
from app.core.exceptions import ClientNotAuthorized, EntityNotFound, InvalidToken
from app.helper.utils import decode_acess_token, decode_url_safe_token
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.shipmentevent import ShipmentEventService
from app.services.delivery_partner import DeliveryPartnerService
from app.services.base import BaseService

# Import from models instead of schemas
from app.database.model import DeliveryPartner, Review, Seller, Shipment, TagName, ShipmentStatus
from app.schemas.schemas import ShipmentCreate, ShipmentRead, ShipmentReview, ShipmentUpdate

from datetime import datetime, timedelta
from app.database.redis import get_shipment_verification_code

class ShipmentService(BaseService):
    def __init__(self, session: AsyncSession, partner_service: DeliveryPartnerService, event_service: ShipmentEventService):
        super().__init__(Shipment, session)
        self.partner_service = partner_service
        self.event_service = event_service

    async def get(self, id: UUID) -> Shipment | None:
        shipment = await self._get(id)
        if not shipment:
            raise EntityNotFound()
        return shipment

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
            raise EntityNotFound()

        if shipment.delivery_partner_id != partner.id:
            raise ClientNotAuthorized()
        if shipment_update.status == ShipmentStatus.delivered:
            code= await get_shipment_verification_code(shipment.id)
            if code!=shipment_update.verification_code:
                raise ClientNotAuthorized()
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

    async def add_tag(self, id: UUID, tag_name: TagName):
        shipment = await self.get(id)
        if shipment is None:
            raise HTTPException(status_code=404, detail="Shipment not found")

        # Get the tag from the database
        tag = await tag_name.tag(self.session)
        if tag is None:
            raise EntityNotFound()
        
        # Check if tag is already associated with shipment to avoid duplicates
        if tag in shipment.tags:
            raise HTTPException(status_code=400, detail=f"Tag '{tag_name.value}' already associated with shipment")
        
        shipment.tags.append(tag)
        await self._update(shipment)
        return shipment

    async def remove_tag(self, id: UUID, tag_name: TagName):
        shipment = await self.get(id)
        if shipment is None:
            raise EntityNotFound()

        # Get the tag from the database
        tag = await tag_name.tag(self.session)
        if tag is None:
            raise EntityNotFound()

        try:
            shipment.tags.remove(tag)
        except ValueError:
            raise EntityNotFound()

        await self._update(shipment)
        return shipment

    async def rate(self,token:str, rating:int,comment:str):
        token_data = decode_url_safe_token(token)
        print("Here is your token ######################----->>>>>>:",token_data)
        if token_data is None:
            raise InvalidToken()
        shipment=await self.get(UUID(token_data["id"]))
        new_review=Review(
           rating=rating,
           comment=comment,
            shipment_id=shipment.id,
        )
        self.session.add(new_review)
        await self.session.commit()
        

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

    async def delete(self, id: int) -> None:
        await self._delete(await self.get(id))