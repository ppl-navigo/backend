from fastapi import HTTPException, status
from datetime import datetime
from jose import JWTError
from app.utils.jwt import (
    create_access_token, create_refresh_token, decode_token,
    is_valid_refresh_token, revoke_refresh_token
)
from app.model.auth.user import User

# For demo purposes only - a simple in-memory user store
# In a real app, this would be a database
USERS = {
    "testuser": User(username="testuser", password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", user_id=1)  # Password: secret
}

class AuthService:
    @staticmethod
    def authenticate_user(username: str, password: str):
        """Authenticate a user by username and password"""
        if username not in USERS:
            return False
        user = USERS[username]
        
        # In a real app, use verify_password(password, user.hashed_password)
        # For simplicity in this demo, we're checking directly
        if password != "secret":  # In real app, use the verify_password function
            return False
        return user
    
    @staticmethod
    def create_tokens(user_id: int):
        """Create access and refresh tokens for a user"""
        access_token = create_access_token(subject=user_id)
        refresh_token, _ = create_refresh_token(subject=user_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def refresh_tokens(refresh_token: str):
        """Generate new tokens using a refresh token"""
        try:
            # Decode token to validate it
            payload = decode_token(refresh_token)
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            # Check token type
            if token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Check if token is in the active tokens list
            if not is_valid_refresh_token(user_id, refresh_token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token expired or revoked",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Revoke the old refresh token
            revoke_refresh_token(user_id)
            
            # Create new tokens
            return AuthService.create_tokens(user_id=int(user_id))
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def logout(refresh_token: str):
        """Logout a user by revoking their refresh token"""
        try:
            # Decode token to get user_id
            payload = decode_token(refresh_token)
            user_id = payload.get("sub")
            
            # Revoke the refresh token
            return revoke_refresh_token(user_id)
            
        except JWTError:
            return False