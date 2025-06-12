from datetime import datetime, timedelta
import jwt
from services.user import UserService
from helper.utils import generate_access_token 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.schemas import SellerCreate
from database.model import Seller
from fastapi import HTTPException, status
from passlib.context import CryptContext
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
class SellerService(UserService):
    def __init__(self, session: AsyncSession):
       super().__init__(Seller, session)
    async def add(self,seller_create:SellerCreate):
       return await self._add_user(seller_create.model_dump())
    async def token(self,email,password)->str:
       return await self._generate_token(email,password)