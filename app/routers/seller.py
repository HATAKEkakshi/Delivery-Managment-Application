from fastapi import APIRouter
from app.api.dependencies import SellerServiceDep
from app.schemas.schemas import SellerRead
from app.schemas.schemas import SellerCreate
seller=APIRouter(prefix="/seller",tags=["Seller"])


@seller.post("/signup",response_model=SellerRead)
async def register_seller(seller:SellerCreate,service:SellerServiceDep):
    return await service.add(seller)
    