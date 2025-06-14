import asyncio
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from database.config import notification_settings

class NotificationService():
    def __init__(self):
        self.fastmail = FastMail(
            ConnectionConfig(
                **notification_settings.model_dump(),
            )
        )

    async def send_message(self, email: str, subject: str, body: str):
        if not email:
            print(f"❌ No email found. Notification not sent.")
            return

        print(f"📬 Sending email to: {email}")

        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=body,
            subtype=MessageType.plain,
        )

        await self.fastmail.send_message(message)
