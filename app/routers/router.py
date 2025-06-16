# app/api/routes/shipment.py

from typing_extensions import Annotated
from uuid import UUID
from database.config import app_settings
from helper.utils import TEMPLATE_DIR
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from api.dependencies import DeliveryPartnerServiceDep, ServiceDep,DeliveryDep
from schemas.schemas import ShipmentCreate, ShipmentReview,ShipmentRead, ShipmentUpdate
from api.dependencies import SellerDep
router = APIRouter(prefix="/shipment",tags=["Shipment"])
templates=Jinja2Templates(TEMPLATE_DIR)
@router.get("/", response_model=ShipmentRead)
async def get_shipment(id: UUID, service: ServiceDep):
    print("here is your argument:",await service.get(id))
    shipment = await service.get(id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment
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