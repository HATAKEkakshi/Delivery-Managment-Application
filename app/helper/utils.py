from datetime import datetime, timedelta,timezone
from database.config import security_settings
import jwt
from uuid import uuid4
from fastapi import HTTPException, status

def generate_access_token(data:dict,expiry:timedelta=timedelta(days=1)) -> str:
    return jwt.encode(
            payload={
                **data,
                "jti":str(uuid4()),
                "exp":datetime.now(timezone.utc)+expiry,  
            },
            algorithm=security_settings.JWT_ALGORITHM,
            key=security_settings.JWT_SECRET,
        )
def decode_acess_token(token:str)->dict | None:
    try:
        return jwt.decode(
            jwt=token,
            key=security_settings.JWT_SECRET,
            algorithms=[security_settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired",
        )
    except jwt.PyJWTError:
        return None
