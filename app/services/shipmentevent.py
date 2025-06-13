import time
from api.shipment import ShipmentStatus
from database.model import Shipment, ShipmentEvent
from services.base import BaseService


class ShipmentEventService(BaseService):
    def __init__(self, session):
        super().__init__(ShipmentEvent, session)

    async def add(self, shipment: Shipment, location: int = None, status: ShipmentStatus = None, description: str = None) -> ShipmentEvent:
        if not location or not status:
            last_event = await self.get_latest_event(shipment)

            if not last_event:
                location = location if location else shipment.destination
                status = status if status else ShipmentStatus.placed
            else:
                location = location if location else last_event.location
                status = status if status else last_event.status

        new_event = ShipmentEvent(
            location=location,
            status=status,
            description=description if description else self._generate_description(status, location),
            shipment_id=shipment.id
        )
        return await self._add(new_event)

    async def get_latest_event(self, shipment: Shipment):
        timeline = getattr(shipment, "timeline", [])
        if not timeline:
            return None
        timeline.sort(key=lambda event: event.created_at)
        return timeline[-1]

    async def _generate_description(self, status: ShipmentStatus, location: int) -> str:
        match status:
            case ShipmentStatus.placed:
                return "assigned to delivery partner."
            case ShipmentStatus.delivered:
                return "Shipment deliverd ."
            case ShipmentStatus.out_for_delivery:
                return "Shipment out for delivery"
            case ShipmentStatus.cancelled:
                return "Shipment cancelled by the seller."
            case _:
                return f"scanned at {location}"
