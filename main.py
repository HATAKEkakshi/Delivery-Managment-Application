from fastapi import FastAPI, APIRouter,Request
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
try:
    from app.worker.tasks import add_log 
except ImportError:
    # Fallback for testing environment
    def add_log(message: str):
        print(f"LOG: {message}")
from scalar_fastapi import get_scalar_api_reference
from app.database.session import create_db_tables
from app.core.exceptions import add_exception_handlers_to_app  # 👈 Import this
from app.routers.router import router
from app.routers.seller import seller
from app.routers.delivery_partner import partner
from fastapi.middleware.cors import CORSMiddleware
from time import perf_counter
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

description = """
 Delivery Management system for sellers and delivery partners.

 ### Sellers:
    - Create and manage shipments.
    - Track shipment status and history.
### Delivery Partners:
    - View assigned shipments.
    - Update shipment status.
    - Email and SMS notifications for shipment updates.

"""

# FastAPI app
app = FastAPI(lifespan=lifespan_handler,
              title="FastShip - Shipment Management Service",
              description=description,
              docs_url="/docs",
              version="0.1.0",
              terms_of_service="https://fastapi.tiangolo.com/terms/",
              contact={
                  "name": "FastShip Support",
                  "url": "https://fastapi.tiangolo.com/contact/",
                  "email": "hemant.kumardeveloper@gmail.com"
              })
app.include_router(master_router)
@app.middleware("http")
async def custom_middleware(request:Request, call_next):
    start=perf_counter()
    response = await call_next(request)
    end=perf_counter()
    duration=round(end-start, 2)
    add_log(f"Request: {request.method} {request.url} - Response Status: {response.status_code} - Duration: {duration:.4f} seconds")
    return response
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Register all exception handlers
add_exception_handlers_to_app(app)  # 👈 THIS LINE IS ESSENTIAL

@app.get("/health", tags=["Health"])
async def health_check():
    return JSONResponse(content={"status": "ok server running"}, status_code=200)
# Scalar Docs
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )
