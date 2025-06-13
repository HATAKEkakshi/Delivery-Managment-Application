from typing import Annotated
from uuid import UUID
from services.shipmentevent import ShipmentEventService
from services.delivery_partner import DeliveryPartnerService
from database.model import DeliveryPartner, Seller, Shipment
from services.seller import SellerService
from fastapi import Depends,HTTPException, status
from helper.utils import decode_acess_token
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import oauth2_scheme_seller,oauth2_scheme_partner
from services.shipment import ShipmentService
from database.session import get_session
from database.redis import is_jti_blacklisted

# Type alias for the async session dependency
SessionDep = Annotated[AsyncSession, Depends(get_session)]
#Acess token data dep
async def _get_acess_token(token:str)->dict:
    data= decode_acess_token(token)
    if data is None or await is_jti_blacklisted(data["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )
    return data
#seller access token 
async def get_seller_acess_token(token: Annotated[str, Depends(oauth2_scheme_seller)]) -> dict:
    return await _get_acess_token(token)
#partner access token
async def get_partner_acess_token(token: Annotated[str, Depends(oauth2_scheme_partner)]) -> dict:
    return await _get_acess_token(token)
##Logged in seller
async def get_current_seller(token_data:Annotated[dict,Depends(get_seller_acess_token)],session:SessionDep):
    seller= await session.get(Seller, UUID(token_data["user"]["id"]))
    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )
    return seller
## logged in partner
async def get_current_partner(token_data:Annotated[dict,Depends(get_partner_acess_token)],session:SessionDep):
    partner= await session.get(DeliveryPartner, UUID(token_data["user"]["id"]))
    if partner is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )
    return partner
# Function to return an instance of ShipmentService with a session
def get_shipment_service(session: SessionDep) -> ShipmentService:
    return ShipmentService(session,DeliveryPartnerService(session),ShipmentEventService(session))
def get_seller_service(session: SessionDep) -> SellerService:
    return SellerService(session)
def get_delivery_partner_service(session: SessionDep):
    return DeliveryPartnerService(session)
# Type alias for injecting the ShipmentService
ServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]

## Seller dep
SellerDep=Annotated[Seller,Depends(get_current_seller)]
DeliveryDep=Annotated[DeliveryPartner,Depends(get_current_partner)]
DeliveryPartnerServiceDep = Annotated[DeliveryPartnerService, Depends(get_delivery_partner_service)]
