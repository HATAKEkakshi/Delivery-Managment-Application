from jinja2 import Environment, FileSystemLoader
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from database.config import notification_settings
from fastapi import BackgroundTasks
from helper.utils import TEMPLATE_DIR
from twilio.rest import Client

import asyncio

class NotificationService:
    def __init__(self, tasks: BackgroundTasks):
        self.tasks = tasks
        self.fastmail = FastMail(
            ConnectionConfig(
                **notification_settings.model_dump(exclude=["TWILIO_SID", "TWILIO_AUTH_TOKEN", "TWILIO_NUMBER"]),
                TEMPLATE_FOLDER=TEMPLATE_DIR,
            )
        )
        self.twilio_client = Client(
            notification_settings.TWILIO_SID,
            notification_settings.TWILIO_AUTH_TOKEN,
        )

    async def _send_plain_email(self, message: MessageSchema):
        await self.fastmail.send_message(message)

    def send_message(self, email: str, subject: str, body: str):
        if not email:
            print("❌ No email found. Notification not sent.")
            return

        print(f"📬 Sending plain text email to: {email}")
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=body,
            subtype=MessageType.plain,
        )

        # ✅ Run async function in thread-safe sync wrapper
        self.tasks.add_task(lambda: asyncio.run(self._send_plain_email(message)))

    async def _send_html_email(self, message: MessageSchema, template_name: str):
        await self.fastmail.send_message(message=message, template_name=template_name)

    def send_email_template(self, email: str, subject: str, context: dict, template_name: str):
        if not email:
            print("❌ No email found. Notification not sent.")
            return

        print(f"📬 Sending HTML email to: {email} using template: {template_name}")
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template(template_name)
        rendered_html = template.render(context)
        print("🔍 Rendered HTML content:\n", rendered_html)

        message = MessageSchema(
            subject=subject,
            recipients=[email],
            template_body=context,
            subtype=MessageType.html,
        )

        self.tasks.add_task(lambda: asyncio.run(self._send_html_email(message, template_name)))

    # ✅ FIXED: SMS must be an instance method INSIDE the class
    def send_sms(self, to: str, body: str):
        if not to:
            print("❌ No phone number found. SMS not sent.")
            return

        print(f"📱 Sending SMS to: {to}")
        try:
            message = self.twilio_client.messages.create(
                body=body,
                from_=notification_settings.TWILIO_NUMBER,
                to=to
            )
            print(f"✅ SMS sent successfully: SID={message.sid}")
        except Exception as e:
            print(f"❌ Failed to send SMS: {e}")
