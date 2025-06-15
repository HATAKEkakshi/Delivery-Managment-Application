from fastapi.security import OAuth2PasswordRequestForm
from typing_extensions import Annotated
from fastapi import APIRouter, Depends,HTTPException, status
from api.dependencies import DeliveryDep, get_partner_acess_token
from database.model import DeliveryPartner
from schemas.schemas import DeliveryPartnerRead, DeliveryPartnerUpdate
from schemas.schemas import DeliveryPartnerCreate
from database.redis import add_jti_to_blacklist
from api.dependencies import DeliveryPartnerServiceDep
partner=APIRouter(prefix="/partner",tags=["Delivery Partner"])


@partner.post("/signup",response_model=DeliveryPartnerRead)
async def register_delivery_partner(seller:DeliveryPartnerCreate,service:DeliveryPartnerServiceDep):
    return await service.add_delivery_partner(seller)
@partner.post("/token")
async def login_delivery_partner(request_form:Annotated[OAuth2PasswordRequestForm,Depends()],service:DeliveryPartnerServiceDep):
    token=await service.generate_token(request_form.username,request_form.password)
    return {
        "access_token":token,
        "type":"jwt"
    }
## Update the delivery partner
@partner.post("/",response_model=DeliveryPartnerRead)
async def update_delivery_partner(partner_update:DeliveryPartnerUpdate,partner:DeliveryDep,service:DeliveryPartnerServiceDep):
    update = partner_update.model_dump(exclude_none=True)
    if not update:
        raise HTTPException(status_code=400, detail="No fields to update")
    return await service.update(partner.sqlmodel_update(update))
@partner.get("/verify")
async def verify_seller_email(token:str,service:DeliveryPartnerServiceDep):
    await service.verify_email(token)
    return {"detail":"Email verified successfully"}
@partner.get("/logout")
async def logout_delivery_partner(token_data:Annotated[dict,Depends(get_partner_acess_token)]):
    await add_jti_to_blacklist(token_data["jti"])
    return{
        "message":"Logged out successfully"
    }