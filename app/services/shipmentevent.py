from random import randint
import time
from app.helper.utils import generate_url_safe_token
from app.database.redis import get_shipment_verification_code,add_shipment_verification_code
from app.schemas.schemas import ShipmentStatus
from app.database.model import Shipment, ShipmentEvent
from app.services.base import BaseService
from app.services.notification import NotificationService
from app.database.config import app_settings
from app.worker.tasks import send_sms,send_email_template
class ShipmentEventService(BaseService):
    def __init__(self, session):
        super().__init__(ShipmentEvent, session)
       # self.notification_service = NotificationService(tasks)

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
        email = shipment.client_email_id
        print(f"###############################Here is the email ######################{email}")

        subject = ""
        context = {}
        template_name = ""

        match status:
            case ShipmentStatus.placed:
                subject = "Shipment Placed"
                context = {
                    "id": shipment.id,
                    "seller": shipment.seller.name,
                    "partner": shipment.delivery_partner.name
                }
                template_name = "mail_placed.html"

            case ShipmentStatus.delivered:
                subject = "Shipment Delivered"
                context["seller"] = shipment.seller.name
                token=generate_url_safe_token({"id":str(shipment.id)})
                context["review_url"]=f"http://{app_settings.APP_DOMAIN}/shipment/review?token={token}"
                template_name = "mail_delivered.html"

            case ShipmentStatus.out_for_delivery:
                subject = "Shipment Out for Delivery"
                template_name = "mail_out_for_delivery.html"
                code=randint(100_000,999_999)
                await add_shipment_verification_code(shipment.id,code)
                if shipment.client_contact_phone:
                    send_sms.delay(
                        to=shipment.client_contact_phone,
                        body=f"Your shipment {shipment.id} is out for delivery. Your verification code is: {code}"
                    )
                else:
                    context["verification_code"] = code
            case ShipmentStatus.cancelled:
                subject = "Shipment Cancelled"
                template_name = "mail_cancelled.html"

            case _:
                (f"⚠️ No email template configured for status: {status}")
                return

        send_email_template.delay(
            email=email,
            subject=subject,
            context=context,
            template_name=template_name
        )

