from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.model.auth.user import UserResponse
from app.model.auth.token import Token, RefreshTokenRequest
from app.services.auth_services import AuthService
from app.middlewares.auth_middleware import get_current_active_user
from app.model.auth.user import User

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = AuthService.authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = AuthService.create_tokens(user_id=user.id)
    return tokens

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshTokenRequest):
    return AuthService.refresh_tokens(refresh_token=refresh_data.refresh_token)

@router.post("/logout")
async def logout(refresh_data: RefreshTokenRequest):
    success = AuthService.logout(refresh_token=refresh_data.refresh_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user