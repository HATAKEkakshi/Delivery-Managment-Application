from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse

from scalar_fastapi import get_scalar_api_reference
from app.database.session import create_db_tables
from app.core.exceptions import add_exception_handlers_to_app  # 👈 Import this
from app.routers.router import router
from app.routers.seller import seller
from app.routers.delivery_partner import partner

# Setup Routers
master_router = APIRouter()
master_router.include_router(router)
master_router.include_router(seller)
master_router.include_router(partner)

# FastAPI lifespan
@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield

# FastAPI app
app = FastAPI(lifespan=lifespan_handler)
app.include_router(master_router)

# Register all exception handlers
add_exception_handlers_to_app(app)  # 👈 THIS LINE IS ESSENTIAL

# Scalar Docs
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )
