# app/api/routes/shipment.py

from typing_extensions import Annotated
from uuid import UUID
from app.database.config import app_settings
from app.database.model import TagName
from app.database.session import SessionDep
from app.helper.utils import TEMPLATE_DIR
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from app.api.dependencies import DeliveryPartnerServiceDep, ServiceDep,DeliveryDep
from app.schemas.schemas import ShipmentCreate, ShipmentReview,ShipmentRead, ShipmentUpdate
from app.api.dependencies import SellerDep
router = APIRouter(prefix="/shipment",tags=["Shipment"])
templates=Jinja2Templates(TEMPLATE_DIR)
@router.get("/", response_model=ShipmentRead)
async def get_shipment(id: UUID, service: ServiceDep):
    return await service.get(id)

@router.get("/track")
async def get_tracking(id: UUID, service: ServiceDep,request:Request):
    shipment=await service.get(id)
    context=shipment.model_dump()
    context["status"]=shipment.status
    context["partner"]=shipment.delivery_partner.name
    context["timeline"]=shipment.timeline
    context["timeline"].reverse()
    return templates.TemplateResponse(
        request=request,
        name="track.html",
        context=context
    )
@router.post("/", response_model=ShipmentRead)
async def submit_shipment(shipment: ShipmentCreate, service: ServiceDep,seller:SellerDep):
    return await service.add(shipment,seller)

@router.patch("/", response_model=ShipmentRead)
async def patch_shipment(
    id: UUID,
    shipment_update: ShipmentUpdate,
    service: ServiceDep,
    partner: DeliveryDep,  # ✅ This gets DeliveryPartner instance
    partner_service: DeliveryPartnerServiceDep,  # ✅ This gets the service
):
    update = shipment_update.model_dump(exclude_none=True)
    if not update:
        raise HTTPException(status_code=400, detail="No fields to update")

    return await service.update(id, shipment_update,partner, partner_service)
@router.get("/tagged",response_model=list[ShipmentRead])
async def get_tagged_shipments(tag_name: TagName, session :SessionDep):
    tag=await tag_name.tag(session)
    return tag.shipments

@router.get("/tag",response_model=ShipmentRead)
async def add_tag_to_shipment(id: UUID,tag_name: TagName,service: ServiceDep):
   return await service.add_tag(id, tag_name)
@router.delete("/tag",response_model=ShipmentRead)
async def remove_tag_from_shipment(id: UUID,tag_name: TagName,service: ServiceDep,):
   return await service.remove_tag(id, tag_name)
@router.get("/cancel",response_model=ShipmentRead)
async def cancel_shipment(id: UUID, seller:SellerDep,service: ServiceDep):
    return await service.cancel(id,seller)
@router.get("/review")
async def submit_review_page(token:str,request:Request):
   return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={ # Placeholder, you can pass actual request if needed
            "review_url": f"http://{app_settings.APP_DOMAIN}/shipment/review?token={token}",
        }
    )

@router.post("/review")
async def submit_review(token:str,rating:Annotated[int,Form(ge=1,le=5)],comment:Annotated[str|None,Form()],service:ServiceDep):
    await service.rate(token,rating,comment)
    return {"detail": "Review submitted successfully"}