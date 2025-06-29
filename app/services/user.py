from datetime import timedelta
from uuid import UUID
from services.notification import NotificationService
from fastapi import BackgroundTasks, HTTPException
from sqlmodel import SQLModel, select
from database.model import User
from helper.utils import generate_access_token,generate_url_safe_token,decode_url_safe_token
from services.base import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from fastapi import status,HTTPException
from database.config import app_settings
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
class UserService(BaseService):
        def __init__(self, model:User,session: AsyncSession,tasks:BackgroundTasks):
            self.model= model
            self.session = session
            self.notification_service = NotificationService(tasks)
        async def _add_user(self,data:dict,router_prefix:str):
             user=self.model(
                  **data,
                  password_hash=password_context.hash(data["password"])
             )
             email=user.email
             user= await self._add(user)
             token=generate_url_safe_token({
                  "email":user.email,
                  "id":str(user.id),
             })
             self.notification_service.send_email_template(
                    email=email,
                    subject="Verify your email",
                    context={
                        "name": user.name,
                        "verification_url": f"http://{app_settings.APP_DOMAIN}/{router_prefix}/verify?token={token}"
                    },
                    template_name="mail_email_verify.html"
             )
             return user
        async def verify_email(self,token:str):
             token_data = decode_url_safe_token(token)
             if token_data is None:
                 raise HTTPException(
                     status_code=status.HTTP_400_BAD_REQUEST,
                     detail="Invalid or expired token"
                 )
            
             user=await self._get( UUID(token_data["id"]))
             user.email_verified = True
             await self._update(user)
        async def _get_by_email(self,email)->User|None:
              return await self.session.scalar(
                    select(self.model).where(self.model.email == email)
              )
        
        async def _get(self, id: UUID) -> User:  # ✅ Added method
            return await self.session.get(self.model, id)
        async def _generate_token(self,email,password)->str:
            user=await self._get_by_email(email)
            if user is None or not password_context.verify(password, user.password_hash):
                raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Email or password is incorrect"
                )
            if not user.email_verified:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email not verified, please verify your email first."
                )
            return generate_access_token(data={"user": {"name": user.name, "email": user.email, "id": str(user.id)}})
        async def send_password_reset_link(self,email,router_prefix:str):
            user=await self._get_by_email(email)
            token=generate_url_safe_token({
                 "id":str(user.id)
            },salt="password-reset")
            self.notification_service.send_email_template(
                email=email,
                subject="Password Reset Request",
                context={
                    "name": user.name,
                    "reset_url": f"http://{app_settings.APP_DOMAIN}{router_prefix}/reset_password_form?token={token}"
                },
                template_name="mail_password_reset.html"
            )
        async def reset_password(self, token: str, password: str)->bool:
            token_data = decode_url_safe_token(token, salt="password-reset", expiry=timedelta(days=1))
            if not token_data:
                return False
            user = await self._get(UUID(token_data["id"]))  
            user.password_hash = password_context.hash(password)
            await self._update(user)
            return True