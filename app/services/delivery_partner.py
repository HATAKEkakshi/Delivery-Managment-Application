from fastapi import HTTPException, status
from sqlalchemy import Sequence
from sqlmodel import select, any_
from database.model import DeliveryPartner, Shipment
from schemas.schemas import DeliveryPartnerCreate
from services.user import UserService


class DeliveryPartnerService(UserService):
    def __init__(self, session,tasks):
        super().__init__(DeliveryPartner, session=session,tasks=tasks)  # DeliveryPartner is a subclass of User

    async def add_delivery_partner(self, delivery_partner: DeliveryPartnerCreate):
        return await self._add_user(delivery_partner.model_dump(),"partner")

    async def get_delivery_partner_by_email(self, email):
        return await self._get_by_email(email)

    async def update(self, partner: DeliveryPartner):
        return await self._update(partner)

    async def get_partners_by_zipcode(self, zipcode: int) -> list[DeliveryPartner]:
        result = await self.session.execute(
            select(DeliveryPartner).where(zipcode == any_(DeliveryPartner.serviceable_zip_codes))
        )
        return result.scalars().all()  # ✅ Return actual model instances

    async def assign_shipment(self, shipment: Shipment):  # ✅ Fixed indentation
        eligible_partners = await self.get_partners_by_zipcode(shipment.destination)
        for partner in eligible_partners:
            if partner.current_handling_capacity > 0:
                partner.shipments.append(shipment)
                return partner
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="No delivery partner available"
        )

    async def generate_token(self, email, password):
        return await self._generate_token(email, password)
         