from fastapi import FastAPI, Request
from fastapi import status,HTTPException

class FastShipError(Exception):
    """Base class for all FastShip exceptions"""
    status=status.HTTP_400_BAD_REQUEST
class EntityNotFound(FastShipError):
    """Raised when an entity is not found in the database"""
    status=status.HTTP_404_NOT_FOUND
class ClientNotAuthorized(FastShipError):
    """Raised when a client is not authorized to perform an action"""
    status=status.HTTP_403_FORBIDDEN
class BadCredentials(FastShipError):
    """Raised when provided credentials are invalid"""
    status=status.HTTP_401_UNAUTHORIZED
class InvalidToken(FastShipError):
    """Raised when access token is invalid or expired"""
    status=status.HTTP_401_UNAUTHORIZED
class DeliveryPartnerNotAvailable(FastShipError):
    """Raised when no delivery partner is available for a shipment"""
    status=status.HTTP_406_NOT_ACCEPTABLE
class DeliveryPartnerCapacityExceeded(FastShipError):
    """Raised when a delivery partner's capacity is exceeded"""
    status=status.HTTP_406_NOT_ACCEPTABLE
def _get_handler(status:int, detail:str):
    """Helper function to create an exception handler"""
    def handler(request:Request, exception:Exception):
        from rich import print,panel
        print(panel(f"Error: {detail}", title="Exception Occurred"))
        raise HTTPException(
            status_code=status,
            detail=detail
        )
    return handler
def add_exception_handlers(app:FastAPI):
    app.add_exception_handler(EntityNotFound,_get_handler(status.HTTP_404_NOT_FOUND,"Entity not found"))
    app.add_exception_handler(ClientNotAuthorized,_get_handler(status.HTTP_403_FORBIDDEN,"Client not authorized"))
    app.add_exception_handler(BadCredentials,_get_handler(status.HTTP_401_UNAUTHORIZED,"Bad credentials"))
    app.add_exception_handler(InvalidToken,_get_handler(status.HTTP_401_UNAUTHORIZED,"Invalid token"))
    app.add_exception_handler(DeliveryPartnerNotAvailable,_get_handler(status.HTTP_503_SERVICE_UNAVAILABLE,"Delivery partner not available"))
    app.add_exception_handler(DeliveryPartnerCapacityExceeded,_get_handler(status.HTTP_503_SERVICE_UNAVAILABLE,"Delivery partner capacity exceeded"))
def add_exception_handlers_to_app(app:FastAPI):
    for subclass in FastShipError.__subclasses__():
        app.add_exception_handler(subclass, _get_handler(subclass.status, subclass.__doc__ ))