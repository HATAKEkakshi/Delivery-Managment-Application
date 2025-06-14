from fastapi import HTTPException
from sqlmodel import SQLModel, select
from database.model import User
from helper.utils import generate_access_token
from services.base import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from fastapi import status,HTTPException
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
class UserService(BaseService):
        def __init__(self, model:User,session: AsyncSession):
            self.model= model
            self.session = session
        async def _add_user(self,data:dict):
             user=self.model(
                  **data,
                  password_hash=password_context.hash(data["password"])
             )
             return await self._add(user)
        async def _get_by_email(self,email)->User|None:
              return await self.session.scalar(
                    select(self.model).where(self.model.email == email)
              )
        async def _generate_token(self,email,password)->str:
            user=await self._get_by_email(email)
            if user is None or not password_context.verify(password, user.password_hash):
                raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Email or password is incorrect"
                )
            return generate_access_token(data={"user": {"name": user.name, "email": user.email, "id": str(user.id)}})
          
        
        