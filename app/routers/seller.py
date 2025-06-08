from fastapi.security import OAuth2PasswordRequestForm
from typing_extensions import Annotated
from fastapi import APIRouter, Depends,HTTPException, status
from api.dependencies import SellerServiceDep, SessionDep
from database.model import Seller
from schemas.schemas import SellerRead
from schemas.schemas import SellerCreate
from helper.utils import decode_acess_token
from core.security import oauth2_scheme
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
@seller.get("/dashboard")
async def get_dashboard(token:Annotated[str,Depends(oauth2_scheme)],session:SessionDep)->Seller:
    data= decode_acess_token(token)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )
    seller= await session.get(Seller, data["user"]["id"])
    return seller