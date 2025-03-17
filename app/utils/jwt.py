import os
from datetime import datetime, timezone, timedelta
from typing import Any, Union, Dict
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# JWT settings - in a real app, these would be in env variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory token storage (for demonstration only)
# In a real app, these would be stored in a database
active_refresh_tokens = {}  # user_id -> {token: str, expires_at: datetime}

def create_access_token(subject: Union[str, Any]) -> str:
    """Create a new access token"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any]) -> tuple:
    """Create a new refresh token"""
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Store token in memory (in a real app, store in database)
    active_refresh_tokens[str(subject)] = {
        "token": encoded_jwt,
        "expires_at": expire
    }
    
    return encoded_jwt, expire

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def decode_token(token: str) -> Dict:
    """Decode and validate a JWT token"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def revoke_refresh_token(user_id: str) -> bool:
    """Revoke a refresh token by removing it from active tokens"""
    if user_id in active_refresh_tokens:
        del active_refresh_tokens[user_id]
        return True
    return False

def is_valid_refresh_token(user_id: str, token: str) -> bool:
    """Check if refresh token is valid"""
    if user_id not in active_refresh_tokens:
        return False
    
    stored_token = active_refresh_tokens[user_id]
    if stored_token["token"] != token:
        return False
    
    if stored_token["expires_at"] < datetime.now():
        # Token expired
        revoke_refresh_token(user_id)
        return False
    
    return True