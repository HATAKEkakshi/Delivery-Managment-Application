from fastapi import APIRouter
from app.routers.router import router
from app.routers.seller import seller


master_router = APIRouter()
master_router.include_router(router)
master_router.include_router(seller)