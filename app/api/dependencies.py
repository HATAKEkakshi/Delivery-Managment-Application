from typing import Annotated
from app.services.seller import SellerService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.shipment import ShipmentService
from app.database.session import get_session

# Type alias for the async session dependency
SessionDep = Annotated[AsyncSession, Depends(get_session)]

# Function to return an instance of ShipmentService with a session
def get_shipment_service(session: SessionDep) -> ShipmentService:
    return ShipmentService(session)
def get_seller_service(session: SessionDep) -> SellerService:
    return SellerService(session)

# Type alias for injecting the ShipmentService
ServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]