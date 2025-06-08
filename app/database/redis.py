from redis.asyncio import Redis
from database.config import db_settings

_token_blacklist=Redis(
    host=db_settings.REDIS_HOST,
    port=db_settings.REDIS_PORT,
    db=0,  # Ensures strings are returned as Python str
)
async def add_jti_to_blacklist(jti: str):
    print(f"Blacklisting JTI: {jti}")
    await _token_blacklist.set(jti, "blacklisted")
    try:
        pong = await _token_blacklist.ping()
        print("Redis connected:", pong)
    except Exception as e:
        print("Redis connection failed:", e)
  
async def is_jti_blacklisted(jti: str) -> bool:
    print(f"Checking if JTI is blacklisted: {jti}")
    return await _token_blacklist.exists(jti)   # Returns True if exists, False otherwise