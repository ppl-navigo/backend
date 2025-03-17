from fastapi import FastAPI, status
from fastapi.testclient import TestClient
import pytest
from app.routers.auth.email_password_auth import router
from app.services.auth_services import AuthService

class DummyUser:
    def __init__(self, id: int = 1):
        self.id = id

class DummyTokens:
    def __init__(self):
        self.access_token = "dummy_access_token"
        self.refresh_token = "dummy_refresh_token"
    def dict(self):
        return {"access_token": self.access_token, "refresh_token": self.refresh_token}

# Create a FastAPI app and include the auth router
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# def test_login_success(monkeypatch):
#     dummy_user = DummyUser()
#     dummy_tokens = DummyTokens()

#     # Patch the authentication and token creation methods
#     monkeypatch.setattr(AuthService, "authenticate_user", lambda username, password: dummy_user)
#     monkeypatch.setattr(AuthService, "create_tokens", lambda user_id: dummy_tokens.dict())

#     response = client.post("/login", data={"username": "testuser", "password": "testpassword"})
#     assert response.status_code == status.HTTP_200_OK

def test_login_failure(monkeypatch):
    # Patch the authenticate_user method to simulate invalid credentials
    monkeypatch.setattr(AuthService, "authenticate_user", lambda username, password: None)

    response = client.post("/login", data={"username": "wronguser", "password": "wrongpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    json_response = response.json()
    assert json_response["detail"] == "Incorrect username or password"
    # Check that the WWW-Authenticate header is set
    assert response.headers.get("www-authenticate") == "Bearer"