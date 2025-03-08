import pytest
import os
from fastapi.testclient import TestClient
from app.main import app
from starlette.datastructures import UploadFile
import io
import fitz  # PyMuPDF
from docx import Document

client = TestClient(app)

@pytest.fixture
def mock_valid_pdf(tmp_path):
    """✅ Generate a valid PDF file for testing."""
    pdf_path = tmp_path / "valid_test_document.pdf"
    doc = fitz.open()  # Create a new PDF
    page = doc.new_page()
    page.insert_text((100, 100), "This is a test PDF document.")  # Add text
    doc.save(str(pdf_path))
    doc.close()

    file = open(pdf_path, "rb")
    yield file
    file.close()
    
@pytest.fixture
def mock_valid_docx(tmp_path):
    """✅ Generate a real, valid DOCX file for testing."""
    docx_path = tmp_path / "valid_test_document.docx"
    doc = Document()
    doc.add_paragraph("This is a test DOCX document.")
    doc.save(str(docx_path))

    file = open(docx_path, "rb")
    yield file
    file.close()

@pytest.fixture
def mock_unsupported_file(tmp_path):
    """❌ Create an unsupported file format (TXT)."""
    unsupported_path = tmp_path / "test.txt"
    unsupported_path.write_text("This is a text file.")
    file = open(unsupported_path, "rb")
    yield file
    file.close()

def test_analyze_pdf_no_mocks(mock_valid_pdf):
    """✅ Ensure full execution of analyze_document with a real PDF."""
    response = client.post("/analyze/", files={"file": mock_valid_pdf})
    assert response.status_code == 200
    assert "risks" in response.json()

def test_analyze_docx_no_mocks(mock_valid_docx):
    """✅ Ensure DOCX files are processed correctly."""
    response = client.post("/analyze/", files={"file": mock_valid_docx})
    assert response.status_code == 200
    assert "risks" in response.json()

@pytest.mark.asyncio
async def test_direct_call_analyze_document():
    """🔥 Directly call analyze_document with a real PDF."""
    from app.routers.analyze import analyze_document

    # Create an in-memory valid PDF using PyMuPDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((100, 100), "This is a test PDF document.")  # Add some text
    pdf_bytes = doc.write()  # Get the bytes of the PDF
    doc.close()

    fake_file = UploadFile(filename="test.pdf", file=io.BytesIO(pdf_bytes))

    response = await analyze_document(fake_file)
    assert "risks" in response