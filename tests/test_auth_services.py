import pytest
from fastapi import HTTPException, status
from jose import JWTError
from unittest.mock import patch
from app.services.auth_services import AuthService

def get_test_tokens():
    return {
        "access_token": "access_token_value",
        "refresh_token": "refresh_token_value",
        "token_type": "bearer"
    }

@patch('app.services.auth_services.decode_token')
@patch('app.services.auth_services.is_valid_refresh_token')
@patch('app.services.auth_services.revoke_refresh_token')
@patch('app.services.auth_services.AuthService.create_tokens')
def test_refresh_tokens_valid(mock_create_tokens, mock_revoke_refresh_token, mock_is_valid_refresh_token, mock_decode_token):
    # Arrange
    payload = {"sub": "1", "type": "refresh"}
    mock_decode_token.return_value = payload
    mock_is_valid_refresh_token.return_value = True
    mock_create_tokens.return_value = get_test_tokens()
    refresh_token = "valid_refresh_token"
    
    # Act
    tokens = AuthService.refresh_tokens(refresh_token)
    
    # Assert
    mock_decode_token.assert_called_with(refresh_token)
    mock_is_valid_refresh_token.assert_called_with("1", refresh_token)
    mock_revoke_refresh_token.assert_called_with("1")
    mock_create_tokens.assert_called_with(user_id=1)
    assert tokens == get_test_tokens()

@patch('app.services.auth_services.decode_token')
def test_refresh_tokens_invalid_token_type(mock_decode_token):
    # Arrange: token with incorrect type (e.g., "access" instead of "refresh")
    payload = {"sub": "1", "type": "access"}
    mock_decode_token.return_value = payload
    refresh_token = "token_with_invalid_type"
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        AuthService.refresh_tokens(refresh_token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token type"

@patch('app.services.auth_services.decode_token')
@patch('app.services.auth_services.is_valid_refresh_token')
def test_refresh_tokens_invalid_active_token(mock_is_valid_refresh_token, mock_decode_token):
    # Arrange: valid refresh token payload but token is not active
    payload = {"sub": "1", "type": "refresh"}
    mock_decode_token.return_value = payload
    mock_is_valid_refresh_token.return_value = False
    refresh_token = "inactive_refresh_token"
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        AuthService.refresh_tokens(refresh_token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Refresh token expired or revoked"

@patch('app.services.auth_services.decode_token', side_effect=JWTError("Invalid token"))
def test_refresh_tokens_jwt_error(mock_decode_token):
    # Arrange: decode_token throws a JWTError
    refresh_token = "malformed_refresh_token"
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        AuthService.refresh_tokens(refresh_token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate refresh token"