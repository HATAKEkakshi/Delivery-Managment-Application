from helper.utils import TEMPLATE_DIR
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, Form,HTTPException, Request, status
from api.dependencies import SellerServiceDep, SessionDep, get_seller_acess_token
from database.model import Seller
from schemas.schemas import SellerRead
from schemas.schemas import SellerCreate
from core.security import oauth2_scheme_seller
from database.redis import add_jti_to_blacklist
from database.config import app_settings
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
@seller.get("/verify")
async def verify_seller_email(token:str,service:SellerServiceDep):
    await service.verify_email(token)
    return {"detail":"Email verified successfully"}
@seller.get("/forgot_password")
async def verify_forgot_password(email:EmailStr,service:SellerServiceDep):
    await service.send_password_reset_link(email,router_prefix="/seller")
    return {"detail":"check your email for the reset link"}
@seller.get("/reset_password_form")
async def reset_password_form(request:Request,token:str):
    templates=Jinja2Templates(TEMPLATE_DIR)
    return templates.TemplateResponse(
        name="reset.html",
        context={
            "request": request,
            "reset_url": f"http://{app_settings.APP_DOMAIN}{seller.prefix}/reset_password?token={token}",
            "token":token
        }
    )
@seller.post("/reset_password")
async def reset_password(token:str,password:Annotated[str,Form()],service:SellerServiceDep,request:Request):
    is_success=await service.reset_password(token,password)
    templates=Jinja2Templates(TEMPLATE_DIR)
    return templates.TemplateResponse(
        request=request,
        name="password/reset_success.html" if is_success else "password/reset_failed.html",
    )
    return {"detail":"Password reset successfully, you can now login with your new password."}
@seller.get("/logout")
async def logout_seller(token_data:Annotated[dict,Depends(get_seller_acess_token)]):
    await add_jti_to_blacklist(token_data["jti"])
    return{
        "message":"Logged out successfully"
    }