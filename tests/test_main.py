from fastapi.testclient import TestClient
from app.main import app
from app.config.graylog import logger

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "MoU Analyzer is running"}

def test_log_middleware(monkeypatch):
    # Mock the logger.info method to check if it's called correctly
    mock_calls = []
    
    def mock_logger_info(message, extra=None):
        mock_calls.append((message, extra))
    
    monkeypatch.setattr(logger, "info", mock_logger_info)
    
    # Make a request to trigger the middleware
    response = client.get("/")
    assert response.status_code == 200
    
    # Verify logger.info was called with correct parameters
    assert len(mock_calls) == 1
    message, extra = mock_calls[0]
    assert message == "http://testserver/"
    assert extra["req"]["method"] == "GET"
    assert extra["req"]["url"] == "http://testserver/"
    assert extra["res"]["status_code"] == 200