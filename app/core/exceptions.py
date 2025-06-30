from fastapi import FastAPI, Request
from fastapi import status,HTTPException

class FastShipError(Exception):
    """Base class for all FastShip exceptions"""

class EntityNotFound(FastShipError):
    """Raised when an entity is not found in the database"""
class ClientNotAuthorized(FastShipError):
    """Raised when a client is not authorized to perform an action"""
class BadCredentials(FastShipError):
    """Raised when provided credentials are invalid"""
class InvalidToken(FastShipError):
    """Raised when access token is invalid or expired"""
class DeliveryPartnerNotAvailable(FastShipError):
    """Raised when no delivery partner is available for a shipment"""
class DeliveryPartnerCapacityExceeded(FastShipError):
    """Raised when a delivery partner's capacity is exceeded"""
def _get_handler(status:int, detail:str):
    """Helper function to create an exception handler"""
    def handler(request:Request, exception:Exception):
        raise HTTPException(
            status_code=status,
            detail=detail
        )
    return handler
def add_exception_handlers(app:FastAPI):
    app.add_exception_handler(EntityNotFound,handler)