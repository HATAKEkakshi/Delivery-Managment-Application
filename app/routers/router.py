# app/api/routes/shipment.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from api.dependencies import DeliveryPartnerServiceDep, ServiceDep,DeliveryDep
from schemas.schemas import ShipmentCreate, ShipmentRead, ShipmentUpdate
from api.dependencies import SellerDep
router = APIRouter(prefix="/shipment",tags=["Shipment"])

@router.get("/", response_model=ShipmentRead)
async def get_shipment(id: UUID, service: ServiceDep,_:SellerDep):
    print("here is your argument:",await service.get(id))
    shipment = await service.get(id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment

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
    
