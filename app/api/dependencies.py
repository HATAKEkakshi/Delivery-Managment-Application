from typing import Annotated
from database.model import Seller
from services.seller import SellerService
from fastapi import Depends,HTTPException, status
from helper.utils import decode_acess_token
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import oauth2_scheme
from services.shipment import ShipmentService
from database.session import get_session
from database.redis import is_jti_blacklisted

# Type alias for the async session dependency
SessionDep = Annotated[AsyncSession, Depends(get_session)]
#Acess token data dep
async def get_acess_token(token:Annotated[str,Depends(oauth2_scheme)])->dict:
    data= decode_acess_token(token)
    if data is None or await is_jti_blacklisted(data["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )
    return data
##Logged in seller
async def get_current_seller(token_data:Annotated[dict,Depends(get_acess_token)],session:SessionDep):
    return await session.get(Seller, token_data["user"]["id"])
# Function to return an instance of ShipmentService with a session
def get_shipment_service(session: SessionDep) -> ShipmentService:
    return ShipmentService(session)
def get_seller_service(session: SessionDep) -> SellerService:
    return SellerService(session)

# Type alias for injecting the ShipmentService
ServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]

## Seller dep
SellerDep=Annotated[Seller,Depends(get_current_seller)]