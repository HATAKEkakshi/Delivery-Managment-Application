from fastapi.security import OAuth2PasswordRequestForm
from typing_extensions import Annotated
from fastapi import APIRouter, Depends,HTTPException, status
from api.dependencies import SellerServiceDep, SessionDep, get_seller_acess_token
from database.model import Seller
from schemas.schemas import SellerRead
from schemas.schemas import SellerCreate
from core.security import oauth2_scheme_seller
from database.redis import add_jti_to_blacklist
seller=APIRouter(prefix="/seller",tags=["Seller"])


@seller.post("/signup",response_model=SellerRead)
async def register_seller(seller:SellerCreate,service:SellerServiceDep):
    return await service.add(seller)
@seller.post("/token")
async def login_seller(request_form:Annotated[OAuth2PasswordRequestForm,Depends()],service:SellerServiceDep):
    token=await service.token(request_form.username,request_form.password)
    return {
        "access_token":token,
        "type":"jwt"
    }
@seller.get("/logout")
async def logout_seller(token_data:Annotated[dict,Depends(get_seller_acess_token)]):
    await add_jti_to_blacklist(token_data["jti"])
    return{
        "message":"Logged out successfully"
    }