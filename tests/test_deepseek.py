import asyncio

from fastapi.testclient import TestClient
from app.main import app
import pytest
from unittest.mock import patch

ROUTE = '/deepseek'
client = TestClient(app)


"""
Test below focus on the second acceptance criteria of PBI "Membuat Dokumen Legal":

Dokumen yang dihasilkan oleh sistem harus sepenuhnya mencerminkan persyaratan yang diberikan oleh pengguna 
dengan probabilitas di atas standar perplexity 0.5 dikali banyaknya kata. 
Jika dokumen tidak sesuai dengan instruksi atau ada elemen yang hilang, 
sistem akan memberikan notifikasi kesalahan dan menawarkan opsi bagi pengguna untuk memperbaiki input 
atau menyarankan pengeditan agar hasil dokumen lebih akurat.
"""


async def mock_deepseek_stream_response(system_prompt, query):
    """Mock DeepSeek's streaming response for testing"""
    for word in ["AI", "Response:", "Sky", "is", "blue."]:
        yield word + " "
        await asyncio.sleep(0.01)


@patch("app.routers.legal_docs_generator.deepseek.deepseek_stream_response")
@pytest.mark.asyncio
async def test_deepseek_streaming_success(mock_deepseek):
    """✅ Should successfully stream DeepSeek responses"""
    mock_deepseek.side_effect = mock_deepseek_stream_response

    request_data = {
        "system_prompt": "Why is the sky blue?",
        "query": "Explain in simple terms."
    }

    with client.stream("POST", ROUTE, json=request_data) as response:
        assert response.status_code == 200  

        chunks = []
        for chunk in response.iter_text():
            chunks.append(chunk)
            assert len(chunk) > 0 
        
        full_response = "".join(chunks)
        assert "AI Response:" in full_response

@patch("app.routers.legal_docs_generator.deepseek.deepseek_stream_response")
@pytest.mark.asyncio
async def test_deepseek_invalid_payload(mock_deepseek):
    """❌ Should return 400 when payload is missing required fields"""
    request_data = {
        "query": "Missing system prompt"  # Missing 'system_prompt'
    }

    response = client.post(ROUTE, json=request_data)
    
    assert response.status_code == 422
    assert "missing" in response.text  # Unprocessable entity, missing system_prompt (failed case)


@patch("app.routers.legal_docs_generator.deepseek.deepseek_stream_response")
@pytest.mark.asyncio
async def test_deepseek_empty_prompt(mock_deepseek):
    """❌ Should return 422 when system prompt is empty"""
    request_data = {
        "system_prompt": "",
        "query": "Explain AI ethics."
    }

    response = client.post(ROUTE, json=request_data)
    
    assert response.status_code == 422
    assert "field required" in response.text # Unprocessable entity, empty system_prompt (corner case)


@patch("app.routers.legal_docs_generator.deepseek.deepseek_stream_response")
@pytest.mark.asyncio
async def test_deepseek_invalid_temperature(mock_deepseek):
    """❌ Should return 422 when temperature is out of range"""
    request_data = {
        "system_prompt": "Describe reinforcement learning.",
        "query": "Explain in 10 words.",
        "temperature": 5.0  # Out of range
    }

    response = client.post(ROUTE, json=request_data)
    
    assert response.status_code == 422
    assert "value is not a valid float" in response.text  # Unprocessable entity, invalid temperature (corner case)

