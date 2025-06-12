from fastapi.security import OAuth2PasswordRequestForm
from typing_extensions import Annotated
from fastapi import APIRouter, Depends,HTTPException, status
from api.dependencies import DeliveryDep, get_partner_acess_token
from database.model import DeliveryPartner
from schemas.schemas import DeliveryPartnerRead, DeliveryPartnerUpdate
from schemas.schemas import DeliveryPartnerCreate
from database.redis import add_jti_to_blacklist
partner=APIRouter(prefix="/partner",tags=["Delivery Partner"])


@partner.post("/signup",response_model=DeliveryPartnerRead)
async def register_delivery_partner(seller:DeliveryPartnerCreate,service):
    return await service.add(seller)
@partner.post("/token")
async def login_delivery_partner(request_form:Annotated[OAuth2PasswordRequestForm,Depends()],service):
    token=await service.token(request_form.username,request_form.password)
    return {
        "access_token":token,
        "type":"jwt"
    }
## Update the delivery partner
@partner.post("/")
async def update_delivery_partner(partner_update:DeliveryPartnerUpdate,partner:DeliveryDep,service):
    pass
@partner.get("/logout")
async def logout_delivery_partner(token_data:Annotated[dict,Depends(get_partner_acess_token)]):
    await add_jti_to_blacklist(token_data["jti"])
    return{
        "message":"Logged out successfully"
    }