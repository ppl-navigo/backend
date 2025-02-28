import os
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from io import BytesIO
import fitz
from app.main import app

client = TestClient(app)
UPLOAD_DIR = "uploads"

@pytest.fixture
def mock_pdf_with_text():
    """Mock PDF file with extractable text."""
    mock_pdf = MagicMock()
    mock_pdf.__enter__.return_value = mock_pdf
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample extracted text from PDF"
    mock_pdf.pages = [mock_page]
    return mock_pdf

def create_valid_pdf():
    """Creates a minimal valid PDF in memory"""
    pdf_stream = BytesIO()
    doc = fitz.open()  # Create a blank PDF
    doc.new_page(width=595, height=842)  # Add a blank A4 page
    doc.save(pdf_stream)
    pdf_stream.seek(0)  # Move cursor to the beginning
    return pdf_stream

def test_upload_valid_pdf():
    """Positive test: Upload a valid PDF under 10MB"""
    pdf_content = create_valid_pdf()
    files = {"file": ("test.pdf", pdf_content, "application/pdf")}
    response = client.post("/upload/", files=files, data={"prompt": "Test prompt"})

    assert response.status_code == 200
    assert "File processed successfully" in response.json().get("message", "")


def test_upload_non_pdf_file():
    """Negative test: Upload a non-PDF file"""
    txt_content = BytesIO(b"Just some text")
    files = {"file": ("test.txt", txt_content, "text/plain")}
    response = client.post("/upload/", files=files, data={"prompt": "Test prompt"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed"

def test_upload_large_pdf():
    """Edge case: Upload a PDF exceeding 10MB"""
    large_pdf_content = BytesIO(b"%PDF-1.4\n" + (b"A" * (10 * 1024 * 1024 + 1)))  # Slightly over 10MB
    files = {"file": ("large.pdf", large_pdf_content, "application/pdf")}
    response = client.post("/upload/", files=files, data={"prompt": "Test prompt"})

    assert response.status_code == 400
    assert response.json()["detail"] == "File size exceeds 10MB limit"

def test_upload_empty_pdf():
    """Edge case: Upload an empty but valid PDF file"""
    valid_empty_pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj <<>> endobj\n"
        b"trailer << /Root 1 0 R >>\n"
        b"%%EOF"
    )  # Proper PDF structure

    empty_pdf_content = BytesIO(valid_empty_pdf)
    files = {"file": ("empty.pdf", empty_pdf_content, "application/pdf")}
    response = client.post("/upload/", files=files, data={"prompt": "Test prompt"})

    assert response.status_code == 200  # Empty PDFs should be processed
    assert response.json()["message"] == "File processed successfully"
