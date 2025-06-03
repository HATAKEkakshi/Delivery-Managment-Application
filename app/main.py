from fastapi import FastAPI, HTTPException, status,Depends
from scalar_fastapi import get_scalar_api_reference
from typing import Any
from contextlib import asynccontextmanager
from .schemas import ShipmentRead, ShipmentCreate, ShipmentUpdate,ShipmentStatus
from .database import Database
from database.session import create_db_tables,get_session, SessionDep
from database.model import Shipment
from sqlalchemy.orm import Session
from datetime import datetime,timedelta
from sqlmodel import SQLModel

@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    create_db_tables()
    yield 

app = FastAPI(lifespan=lifespan_handler)
db = Database()


@app.get("/shipment/latest", response_model=ShipmentRead)
def get_latest_shipment() -> dict[str, Any]:
    # Get the latest ID from the DB
    db.cur.execute("SELECT MAX(id) FROM shipment")
    result = db.cur.fetchone()
    if not result or result[0] is None:
        raise HTTPException(status_code=404, detail="No shipments found")
    latest_id = result[0]
    shipment = db.get(latest_id)
    return shipment


@app.get("/shipment", response_model=ShipmentRead)
def get_shipment(id: int,session:SessionDep):
    shipment = session.get(Shipment,id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    return shipment


@app.post("/shipment")
def submit_shipment(shipment: ShipmentCreate,session:SessionDep) -> dict[str, Any]:
    new_shipment= Shipment(
        **shipment.model_dump(),
          status=ShipmentStatus.placed,
          estimated_delivery_date=datetime.now()+timedelta(days=3)
            # Unpack the ShipmentCreate model
    )
    session.add(new_shipment)
    session.commit()
    session.refresh(new_shipment)
    return {"id": new_shipment.id}


@app.put("/shipment", response_model=ShipmentRead)
def shipment_update(id: int, shipment: ShipmentCreate) -> dict[str, Any]:
    # Using full update
    db.update(id, ShipmentUpdate(status=shipment.status))  # if status only
    return db.get(id)


@app.patch("/shipment", response_model=ShipmentRead)
def patch_shipment(id: int, shipment_update: ShipmentUpdate,session:SessionDep):
    update=shipment_update.model_dump(exclude_none=True)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    shipment = session.get(Shipment, id)
    shipment.sqlmodel_update(update)
    session.add(shipment)
    session.commit()
    session.refresh(shipment)
    return shipment


@app.delete("/shipment")
def delete_shipment(id: int,session:SessionDep) -> dict[str, str]:
    session.delete(
        session.get(Shipment,id)
    )
    session.commit()
    return {"message": "Shipment deleted successfully"}


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )
