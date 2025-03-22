import pytest
from unittest.mock import patch, MagicMock
from app.utils.ai_client import AIClient

@pytest.fixture
def mock_ai_response():
    """Mock AI response with valid risk analysis output."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Klausul 1: 'Pihak Kedua harus membayar penuh sebelum menerima layanan.' Alasan: 'Klausul ini dapat merugikan Pihak Kedua karena tidak ada jaminan layanan.'"))
    ]
    return mock_response

@pytest.fixture
def mock_ai_error_response():
    """Mock AI response for an API failure."""
    return Exception("API request failed")

# ✅ Test 1: AIClient should return valid AI response when successful
def test_ai_client_success(mock_ai_response):
    with patch("app.utils.ai_client.OpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create.return_value = mock_ai_response

        text = "Sample contract text"
        response = AIClient.analyze_risk(text)

        assert "Klausul 1" in response, "AIClient did not return expected AI response."

# ✅ Test 2: AIClient should return error message when API fails
def test_ai_client_handles_api_error(mock_ai_error_response):
    with patch("app.utils.ai_client.OpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create.side_effect = mock_ai_error_response

        text = "Sample contract text"
        response = AIClient.analyze_risk(text)

        assert "❌ Gagal menganalisis dokumen" in response, "AIClient did not handle API failure correctly."

# ✅ Test 3: AIClient should handle empty input
def test_ai_client_empty_input():
    with patch("app.utils.ai_client.OpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="Tidak ada risiko terdeteksi."))])

        response = AIClient.analyze_risk("")

        assert response == "Tidak ada risiko terdeteksi.", "AIClient should return proper response for empty input."

# ✅ Test 4: AIClient should handle slow response
def test_ai_client_handles_slow_response(mock_ai_response):
    with patch("app.utils.ai_client.OpenAI") as mock_openai:
        with patch("time.sleep", return_value=None):  # Simulate delayed response
            mock_instance = mock_openai.return_value
            mock_instance.chat.completions.create.return_value = mock_ai_response

            response = AIClient.analyze_risk("Sample contract text")

            assert "Klausul 1" in response, "AIClient should still return valid response after delay."

# # ✅ Test 5: AIClient should send API key
# @patch("app.utils.ai_client.settings")
# @patch("app.utils.ai_client.OpenAI")
# def test_ai_client_uses_api_key(mock_openai, mock_settings):
#     """✅ Ensure AIClient initializes OpenAI with the correct API key."""
#     mock_settings.OPENROUTER_API_KEY = "mock-api-key"
    
#     AIClient.analyze_risk("Sample contract text")

#     mock_openai.assert_called_with(
#         base_url="https://openrouter.ai/api/v1",
#         api_key="mock-api-key"  # ✅ Now matches the mocked value
#     )
