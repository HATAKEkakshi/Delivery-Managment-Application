from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import SellerCreate
from app.database.model import Seller
from passlib.context import CryptContext
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
class SellerService:
    def __init__(self, session: AsyncSession):
        self.session = session
    async def add(self,credentials:SellerCreate):
        seller=Seller(
            **credentials.model_dump(exclude={"password"}),
            ##Hashed password
             password_hash=password_context.hash(credentials.password)
        )
        self.session.add(seller)
        await self.session.commit()
        await self.session.refresh(seller)
        return seller