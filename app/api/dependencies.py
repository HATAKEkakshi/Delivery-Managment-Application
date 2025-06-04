from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.shipment import ShipmentService
from database.session import get_session

# Type alias for the async session dependency
SessionDep = Annotated[AsyncSession, Depends(get_session)]

# Function to return an instance of ShipmentService with a session
def get_shipment_service(session: SessionDep) -> ShipmentService:
    return ShipmentService(session)

# Type alias for injecting the ShipmentService
ServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]
