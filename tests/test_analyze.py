import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_pdf_file(tmp_path):
    """Create a temporary valid PDF file for testing."""
    pdf_path = tmp_path / "test_document.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 Valid PDF content")
    file = open(pdf_path, "rb")
    yield file
    file.close()

@pytest.fixture
def mock_docx_file(tmp_path):
    """Create a temporary valid DOCX file for testing."""
    docx_path = tmp_path / "test_document.docx"
    docx_path.write_bytes(b"PK\x03\x04 Valid DOCX content")
    file = open(docx_path, "rb")
    yield file
    file.close()

@pytest.fixture
def mock_corrupt_pdf(tmp_path):
    """Create a corrupted PDF file."""
    corrupt_pdf_path = tmp_path / "corrupt.pdf"
    corrupt_pdf_path.write_bytes(b"Invalid content")
    file = open(corrupt_pdf_path, "rb")
    yield file
    file.close()

@pytest.fixture
def mock_unsupported_file(tmp_path):
    """Create an unsupported file format (TXT)."""
    unsupported_path = tmp_path / "test.txt"
    unsupported_path.write_text("This is a text file.")
    file = open(unsupported_path, "rb")
    yield file
    file.close()

# ==========================
# ✅ Success Cases
# ==========================
@patch("app.utils.parsers.ParserFactory.get_parser")
@patch("app.utils.ai_client.AIClient.analyze_risk")
@patch("app.utils.risk_parser.RiskParser.parse_ai_risk_analysis")
def test_analyze_pdf_success(mock_risk_parser, mock_ai_client, mock_parser, mock_pdf_file):
    """✅ Successfully process a valid PDF file."""
    mock_parser.return_value.extract_text.return_value = "Extracted text from PDF"
    mock_ai_client.return_value = "AI analyzed risks"
    mock_risk_parser.return_value = [{"clause": "Klausul 1", "risky_text": "Example", "reason": "Example reason"}]

    response = client.post("/analyze/", files={"file": mock_pdf_file})
    
    assert response.status_code == 200
    assert response.json() == {"risks": [{"clause": "Klausul 1", "risky_text": "Example", "reason": "Example reason"}]}

@patch("app.utils.parsers.ParserFactory.get_parser")
@patch("app.utils.ai_client.AIClient.analyze_risk")
@patch("app.utils.risk_parser.RiskParser.parse_ai_risk_analysis")
def test_analyze_docx_success(mock_risk_parser, mock_ai_client, mock_parser, mock_docx_file):
    """✅ Successfully process a valid DOCX file."""
    mock_parser.return_value.extract_text.return_value = "Extracted text from DOCX"
    mock_ai_client.return_value = "AI analyzed risks"
    mock_risk_parser.return_value = [{"clause": "Klausul 2", "risky_text": "Example text", "reason": "Example reason"}]

    response = client.post("/analyze/", files={"file": mock_docx_file})
    
    assert response.status_code == 200
    assert response.json() == {"risks": [{"clause": "Klausul 2", "risky_text": "Example text", "reason": "Example reason"}]}

# ==========================
# ❌ Error Handling Cases
# ==========================
def test_analyze_unsupported_format(mock_unsupported_file):
    """❌ Rejects unsupported file formats like TXT."""
    response = client.post("/analyze/", files={"file": mock_unsupported_file})
    
    assert response.status_code == 400
    assert response.json()["detail"] == "❌ Only PDF and DOCX files are supported."

@patch("app.utils.parsers.ParserFactory.get_parser")
def test_analyze_corrupt_pdf(mock_parser, mock_corrupt_pdf):
    """❌ Handles failure when trying to parse a corrupted PDF."""
    mock_parser.return_value.extract_text.return_value = "❌ Gagal mengekstrak teks atau dokumen kosong."
    
    response = client.post("/analyze/", files={"file": mock_corrupt_pdf})
    
    assert response.status_code == 500
    assert response.json()["detail"] == "❌ Failed to extract text."

@patch("app.utils.parsers.ParserFactory.get_parser")
@patch("app.utils.ai_client.AIClient.analyze_risk", side_effect=Exception("AI service error"))
def test_analyze_ai_failure(mock_ai_client, mock_parser, mock_pdf_file):
    """❌ Handles AI response failure gracefully."""
    mock_parser.return_value.extract_text.return_value = "Extracted text from PDF"
    
    response = client.post("/analyze/", files={"file": mock_pdf_file})
    
    assert response.status_code == 500
    assert response.json()["detail"] == "❌ AI Analysis Failed: AI service error"

# ==========================
# ✅ AI & RiskParser Behavior
# ==========================
@patch("app.utils.parsers.ParserFactory.get_parser")
@patch("app.utils.ai_client.AIClient.analyze_risk")
@patch("app.utils.risk_parser.RiskParser.parse_ai_risk_analysis")
def test_ai_client_called_with_correct_text(mock_risk_parser, mock_ai_client, mock_parser, mock_pdf_file):
    """✅ Ensures AIClient is called with extracted text."""
    extracted_text = "Sample contract text"
    mock_parser.return_value.extract_text.return_value = extracted_text
    mock_ai_client.return_value = "AI analyzed text"
    mock_risk_parser.return_value = [{"clause": "Klausul 3", "risky_text": "Some risk", "reason": "Some reason"}]

    response = client.post("/analyze/", files={"file": mock_pdf_file})
    
    mock_ai_client.assert_called_once_with(extracted_text)
    assert response.status_code == 200

@patch("app.utils.parsers.ParserFactory.get_parser")
@patch("app.utils.ai_client.AIClient.analyze_risk")
@patch("app.utils.risk_parser.RiskParser.parse_ai_risk_analysis")
def test_risk_parser_called_with_ai_response(mock_risk_parser, mock_ai_client, mock_parser, mock_pdf_file):
    """✅ Ensures RiskParser is called with AI response."""
    extracted_text = "Extracted contract"
    ai_response = "AI generated risks"
    mock_parser.return_value.extract_text.return_value = extracted_text
    mock_ai_client.return_value = ai_response
    mock_risk_parser.return_value = [{"clause": "Klausul 4", "risky_text": "Clause risk", "reason": "Clause reason"}]

    response = client.post("/analyze/", files={"file": mock_pdf_file})
    
    mock_risk_parser.assert_called_once_with(ai_response)
    assert response.status_code == 200
