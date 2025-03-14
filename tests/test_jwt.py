import os
import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.utils import jwt as jwt_utils

# Force a test secret key for consistent testing
TEST_SECRET_KEY = "test-secret"
jwt_utils.SECRET_KEY = TEST_SECRET_KEY

@pytest.fixture(autouse=True)
def cleanup_active_refresh_tokens():
    # Ensure active_refresh_tokens is empty before each test
    jwt_utils.active_refresh_tokens.clear()
    yield
    jwt_utils.active_refresh_tokens.clear()

def test_create_access_token():
    subject = "user123"
    token = jwt_utils.create_access_token(subject)
    payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=[jwt_utils.ALGORITHM])
    
    assert payload["sub"] == subject
    assert payload["type"] == "access"
    # Check expiration is within acceptable range
    exp = datetime.fromtimestamp(payload["exp"])
    expected = datetime.utcnow() + timedelta(minutes=jwt_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    assert exp - expected < timedelta(seconds=5)

def test_create_refresh_token():
    subject = "user456"
    token, expire = jwt_utils.create_refresh_token(subject)
    payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=[jwt_utils.ALGORITHM])
    
    assert payload["sub"] == subject
    assert payload["type"] == "refresh"
    # Check expiration is within acceptable range
    exp_timestamp = payload["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    expected = datetime.utcnow() + timedelta(days=jwt_utils.REFRESH_TOKEN_EXPIRE_DAYS)
    assert exp_datetime - expected < timedelta(seconds=5)
    
    # Ensure the token is stored in memory for the subject
    assert subject in jwt_utils.active_refresh_tokens
    stored = jwt_utils.active_refresh_tokens[subject]
    assert stored["token"] == token
    assert stored["expires_at"] == expire

def test_password_hash_and_verify():
    password = "supersecret"
    hashed = jwt_utils.get_password_hash(password)
    assert isinstance(hashed, str)
    # Correct password verification
    assert jwt_utils.verify_password(password, hashed)
    # Incorrect password verification
    assert not jwt_utils.verify_password("wrongpassword", hashed)

def test_decode_token():
    subject = "testuser"
    token = jwt_utils.create_access_token(subject)
    decoded = jwt_utils.decode_token(token)
    assert decoded["sub"] == subject
    assert decoded["type"] == "access"

def test_decode_invalid_token():
    invalid_token = "this.is.an.invalid.token"
    with pytest.raises(JWTError):
        jwt_utils.decode_token(invalid_token)

def test_revoke_refresh_token_and_validation():
    user_id = "user789"
    token, expire = jwt_utils.create_refresh_token(user_id)
    
    # Initially token should be valid
    assert jwt_utils.is_valid_refresh_token(user_id, token)
    
    # Revoke token; subsequent validation should fail
    assert jwt_utils.revoke_refresh_token(user_id)
    assert not jwt_utils.is_valid_refresh_token(user_id, token)

def test_expired_refresh_token(monkeypatch):
    user_id = "user_expired"
    token, expire = jwt_utils.create_refresh_token(user_id)
    
    # Patch datetime to simulate token expiry by moving ahead in time.
    class FakeDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return expire + timedelta(seconds=1)
    
    monkeypatch.setattr(jwt_utils, "datetime", FakeDatetime)
    
    # Now is_valid_refresh_token should fail because token is expired.
    assert not jwt_utils.is_valid_refresh_token(user_id, token)
    # Ensure token is removed from active_refresh_tokens
    assert user_id not in jwt_utils.active_refresh_tokens