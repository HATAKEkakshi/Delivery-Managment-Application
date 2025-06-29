from datetime import datetime, timedelta,timezone

from itsdangerous import BadSignature, Serializer, SignatureExpired, URLSafeSerializer, URLSafeTimedSerializer
from app.database.config import security_settings
from pathlib import Path
import jwt
from uuid import uuid4
from fastapi import HTTPException, status

APP_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = APP_DIR.parent / "templates"
_serializer=URLSafeTimedSerializer(security_settings.JWT_SECRET)

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
def generate_url_safe_token(data:dict,salt:str|None=None)->str:
    return _serializer.dumps(data,salt=salt)
def decode_url_safe_token(token:str,salt:str|None=None,expiry:timedelta|None=None)->dict|None:
    try:
     return _serializer.loads(token,salt=salt,max_age=expiry.total_seconds() if expiry else None)
    except(BadSignature,SignatureExpired):
        return None