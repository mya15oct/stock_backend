from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
import logging

logger = logging.getLogger(__name__)

def create_access_token(data: Dict[str, Any], secret_key: str, algorithm: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token.
    """
    to_encode = data.copy()
    
    # FORCE UTC TIMEZONE AWARENESS
    now_utc = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=1440) # Default 24h
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    
    # SELF-VERIFICATION LOGGING
    try:
        decoded = jwt.decode(encoded_jwt, secret_key, algorithms=[algorithm])
        logger.info(f"Token DEBUG: Created at {now_utc}, Expire CLAIM {expire}, Decoded EXP {decoded.get('exp')}")
    except Exception as e:
        logger.error(f"Token DEBUG: Immediate decode failed! {e}")
        
    return encoded_jwt

def decode_access_token(token: str, secret_key: str, algorithm: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT access token.
    Returns the payload if valid, None otherwise.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError as e:
        logger.warning(f"JWT Decode Error: {e}")
        return None
