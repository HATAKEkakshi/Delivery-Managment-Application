from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference
from app.core.exceptions import InvalidToken
from app.database.session import create_db_tables
from fastapi import APIRouter
from app.routers.router import router
from app.routers.seller import seller
from app.routers.delivery_partner import partner

master_router = APIRouter()
master_router.include_router(router)
master_router.include_router(seller)
master_router.include_router(partner)
@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield

app = FastAPI(lifespan=lifespan_handler)
app.include_router(master_router)
def handler(request,exception):
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid or expired access token"}
    )
app.add_exception_handler(
    InvalidToken,
    handler
)
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )
