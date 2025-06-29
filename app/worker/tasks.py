from celery import Celery
import asyncio
from jinja2 import Environment, FileSystemLoader
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from app.database.config import db_settings, notification_settings
from app.helper.utils import TEMPLATE_DIR
from twilio.rest import Client

# Configure FastMail
fast_mail = FastMail(
    ConnectionConfig(
        **notification_settings.model_dump(exclude={"TWILIO_SID", "TWILIO_AUTH_TOKEN", "TWILIO_NUMBER"}),
        TEMPLATE_FOLDER=TEMPLATE_DIR,
    )
)

# Configure Twilio client
twilio_client = Client(
    notification_settings.TWILIO_SID,
    notification_settings.TWILIO_AUTH_TOKEN,
)

# Initialize Celery
app = Celery(
    "api_tasks",
    broker=db_settings.REDIS_URL(9),
    backend=db_settings.REDIS_URL(9),
)

# ✅ Plain text email task
@app.task
def send_mail(recipients: list[str], subject: str, body: str):
    try:
        message = MessageSchema(
            recipients=recipients,
            subject=subject,
            body=body,
            subtype=MessageType.plain,
        )
        asyncio.run(fast_mail.send_message(message))
        return "Plain text email sent successfully"
    except Exception as e:
        print(f"❌ Error sending plain text email: {e}")
        return f"Failed to send plain text email: {e}"

# ✅ HTML email with Jinja2 template task
@app.task
def send_email_template_task(email: str, subject: str, context: dict, template_name: str):
    if not email:
        print("❌ No email found. Notification not sent.")
        return "No email provided"

    try:
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

        asyncio.run(fast_mail.send_message(message=message, template_name=template_name))
        return "HTML email sent successfully"
    except Exception as e:
        print(f"❌ Error sending template email: {e}")
        return f"Failed to send HTML email: {e}"

# ✅ Twilio SMS task
@app.task
def send_sms(to: str, body: str):
    if not to:
        print("❌ No phone number found. SMS not sent.")
        return "No phone number provided"

    print(f"📱 Sending SMS to: {to}")
    try:
        message = twilio_client.messages.create(
            body=body,
            from_=notification_settings.TWILIO_NUMBER,
            to=to
        )
        print(f"✅ SMS sent successfully: SID={message.sid}")
        return f"SMS sent: SID={message.sid}"
    except Exception as e:
        print(f"❌ Failed to send SMS: {e}")
        return f"Failed to send SMS: {e}"