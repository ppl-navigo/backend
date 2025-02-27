import pytest
from unittest.mock import patch, MagicMock
from app.utils.pdf_parser import extract_text_pdf

@pytest.fixture
def mock_pdf_with_text():
    """Mock PDF file with extractable text."""
    mock_pdf = MagicMock()
    mock_pdf.__enter__.return_value = mock_pdf  
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample extracted text from PDF"
    mock_pdf.pages = [mock_page]
    return mock_pdf

@pytest.fixture
def mock_pdf_no_text():
    """Mock PDF file with no extractable text."""
    mock_pdf = MagicMock()
    mock_pdf.__enter__.return_value = mock_pdf
    mock_page = MagicMock()
    mock_page.extract_text.return_value = None
    mock_pdf.pages = [mock_page]
    return mock_pdf

def test_extract_text_pdf_with_text(mock_pdf_with_text):
    """Test PDF with extractable text."""
    with patch("pdfplumber.open", return_value=mock_pdf_with_text):
        extracted_text = extract_text_pdf("dummy.pdf")
        assert extracted_text == "Sample extracted text from PDF", f"Unexpected output: {extracted_text}"

def test_extract_text_pdf_no_text(mock_pdf_no_text):
    """Test PDF with no text."""
    with patch("pdfplumber.open", return_value=mock_pdf_no_text):
        extracted_text = extract_text_pdf("dummy.pdf")
        assert extracted_text == "❌ Gagal mengekstrak teks atau dokumen kosong."

def test_extract_text_pdf_unsupported_format():
    """Test unsupported file format (e.g., .jpg, .xls)."""
    with pytest.raises(Exception): 
        extract_text_pdf("dummy.jpg")

def test_extract_text_pdf_corrupted_file():
    """Test corrupted PDF file."""
    with patch("pdfplumber.open", side_effect=Exception("Corrupted file")):
        with pytest.raises(Exception, match="Corrupted file"):
            extract_text_pdf("corrupted.pdf")
