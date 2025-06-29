from celery import Celery
import asyncio
from jinja2 import Environment, FileSystemLoader
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from app.database.config import db_settings, notification_settings
from app.helper.utils import TEMPLATE_DIR
from twilio.rest import Client

# --- Mail Configuration ---
fast_mail = FastMail(
    ConnectionConfig(
        **notification_settings.model_dump(
            exclude={"TWILIO_SID", "TWILIO_AUTH_TOKEN", "TWILIO_NUMBER"}
        ),
        TEMPLATE_FOLDER=TEMPLATE_DIR,
    )
)

# --- Twilio Client Setup ---
twilio_client = Client(
    notification_settings.TWILIO_SID,
    notification_settings.TWILIO_AUTH_TOKEN,
)

# --- Celery App ---
celery_app = Celery(
    "notifications",
    broker=db_settings.REDIS_URL(9),
    backend=db_settings.REDIS_URL(9),
    broker_connection_retry_on_startup=True,
)

# ✅ Plain Text Email Task
@celery_app.task(name="notifications.send_plain_email")
def send_plain_email(recipients: list[str], subject: str, body: str):
    try:
        message = MessageSchema(
            recipients=recipients,
            subject=subject,
            body=body,
            subtype=MessageType.plain,
        )
        asyncio.run(fast_mail.send_message(message))
        return "✅ Plain text email sent"
    except Exception as e:
        print(f"❌ Error sending plain text email: {e}")
        return f"❌ Failed: {e}"

# ✅ HTML Email Task (with template)
@celery_app.task(name="notifications.send_template_email")
def send_email_template(email: str, subject: str, context: dict, template_name: str):
    if not email:
        return "❌ No recipient email provided"

    try:
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template(template_name)
        rendered = template.render(context)

        message = MessageSchema(
            subject=subject,
            recipients=[email],
            template_body=context,
            subtype=MessageType.html,
        )

        asyncio.run(fast_mail.send_message(message=message, template_name=template_name))
        return "✅ HTML email sent"
    except Exception as e:
        print(f"❌ Error sending HTML email: {e}")
        return f"❌ Failed: {e}"

# ✅ SMS Task
@celery_app.task(name="notifications.send_sms")
def send_sms(to: str, body: str):
    if not to:
        return "❌ No phone number provided"

    try:
        message = twilio_client.messages.create(
            body=body,
            from_=notification_settings.TWILIO_NUMBER,
            to=to
        )
        return f"✅ SMS sent: SID={message.sid}"
    except Exception as e:
        print(f"❌ SMS send error: {e}")
        return f"❌ Failed: {e}"
