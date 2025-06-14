import time
from api.shipment import ShipmentStatus
from database.model import Shipment, ShipmentEvent
from services.base import BaseService
from services.notification import NotificationService

class ShipmentEventService(BaseService):
    def __init__(self, session):
        super().__init__(ShipmentEvent, session)
        self.notification_service = NotificationService()

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
            description=description or await self._generate_description(status, location),
            shipment_id=shipment.id
        )

        await self.notify(shipment, status)
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
                return "Shipment delivered."
            case ShipmentStatus.out_for_delivery:
                return "Shipment out for delivery"
            case ShipmentStatus.cancelled:
                return "Shipment cancelled by the seller."
            case _:
                return f"scanned at {location}"

    async def notify(self, shipment: Shipment, status: ShipmentStatus):
        # ✅ Use the correct field name
        email = shipment.client_email_id
        print(f"###############################Here is the email ######################{email}")
        match status:
            case ShipmentStatus.placed:
                await self.notification_service.send_message(
                    email=email,
                    subject="Shipment Placed",
                    body=f"Your order is with the seller {shipment.seller.name} and will be delivered by {shipment.delivery_partner.name}."
                )
            case ShipmentStatus.delivered:
                await self.notification_service.send_message(
                    email=email,
                    subject="Shipment Delivered",
                    body=f"Your order has been delivered by {shipment.delivery_partner.name}."
                )
            case ShipmentStatus.out_for_delivery:
                await self.notification_service.send_message(
                    email=email,
                    subject="Shipment Out for Delivery",
                    body=f"Your order is out for delivery by {shipment.delivery_partner.name}."
                )
            case ShipmentStatus.cancelled:
                await self.notification_service.send_message(
                    email=email,
                    subject="Shipment Cancelled",
                    body=f"Your order has been cancelled by the seller {shipment.seller.name}."
                )
