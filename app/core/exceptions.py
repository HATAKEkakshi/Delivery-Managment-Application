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