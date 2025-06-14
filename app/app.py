import asyncio
import fastapi
from fastapi_mail import ConnectionConfig,FastMail,MessageSchema, MessageType
from database.config import notification_settings

fastmail=FastMail(
    ConnectionConfig(
       **notification_settings.model_dump(),
    )
)
async def send_message():
    await fastmail.send_message(
        message=MessageSchema(
            recipients=["hemant.kumardeveloper@gmail.com"],
            subject="Your Mail from fastship",
            body="Yoi lets go you are going to send a email",
            subtype=MessageType.plain,))
    print("Mail sent successfully")
asyncio.run(send_message())

