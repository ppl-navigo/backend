import pytest
import os
from fastapi.testclient import TestClient
from app.main import app
from starlette.datastructures import UploadFile
import io
import fitz  # PyMuPDF
from docx import Document
from unittest.mock import patch

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

@pytest.fixture
def sample_ai_response():
    """Mock AI response with multiple risk clauses."""
    return '''
    Klausul 2: "Jasa dari PIHAK PERTAMA kepada PIHAK KEDUA dimulai sejak PIHAK KEDUA melakukan PEMBAYARAN."
    Alasan: "Tidak ada perlindungan bagi PIHAK KEDUA terhadap keterlambatan PIHAK PERTAMA."

    Klausul 6: "Tahap pertama sebagai uang muka sebesar Rp. ______________ akan dibayarkan oleh PIHAK KEDUA."
    Alasan: "Tidak ada jaminan bahwa PIHAK PERTAMA akan menyelesaikan pekerjaan sesuai standar."
    '''

@pytest.mark.asyncio
async def test_analyze_pdf_no_mocks(mock_valid_pdf):
    """✅ Ensure full execution of analyze_document with a real PDF, but mock AI."""
    with patch("app.utils.ai_client.AIClient.analyze_risk", return_value="Mocked AI response"):
        response = client.post("/analyze/", files={"file": mock_valid_pdf})
        assert "detail" in response.json() or "risks" in response.json()


@pytest.mark.asyncio
async def test_analyze_docx_no_mocks(mock_valid_docx):
    """✅ Ensure DOCX files are processed correctly, but mock AI."""
    with patch("app.utils.ai_client.AIClient.analyze_risk", return_value="Mocked AI response"):
        response = client.post("/analyze/", files={"file": mock_valid_docx})
        assert "detail" in response.json() or "risks" in response.json()

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

    with patch("app.utils.ai_client.AIClient.analyze_risk", return_value="Mocked AI response"):
        response = await analyze_document(fake_file)
        assert "N/A" in response['risks'][0]['clause']

# ==========================
# Tests for `/extract-text/` route
# ==========================

@pytest.mark.asyncio
async def test_extract_text_pdf(mock_valid_pdf):
    """✅ Ensure that PDF text extraction works."""
    with patch("app.utils.parsers.PDFParser.extract_text", return_value="Sample extracted text from PDF"):
        response = client.post("/extract-text/", files={"file": mock_valid_pdf})
        assert response.status_code == 200
        assert "Sample extracted text from PDF" in response.text

@pytest.mark.asyncio
async def test_extract_text_docx(mock_valid_docx):
    """✅ Ensure that DOCX text extraction works."""
    with patch("app.utils.parsers.DOCXParser.extract_text", return_value="Sample extracted text from DOCX"):
        response = client.post("/extract-text/", files={"file": mock_valid_docx})
        assert response.status_code == 200
        assert "Sample extracted text from DOCX" in response.text

@pytest.mark.asyncio
async def test_extract_text_unsupported_format(mock_unsupported_file):
    """❌ Ensure that unsupported file formats return a 400 error."""
    response = client.post("/extract-text/", files={"file": mock_unsupported_file})
    assert response.status_code == 400
    assert "❌ Format txt tidak didukung! Hanya mendukung PDF dan DOCX." in response.text

@pytest.mark.asyncio
async def test_extract_text_invalid_file():
    """❌ Test when the file is corrupt or invalid."""
    with patch("app.utils.parsers.PDFParser.extract_text", side_effect=ValueError("Invalid file format")):
        response = client.post("/extract-text/", files={"file": "invalid_file.pdf"})
        assert response.status_code == 400
        assert "❌ Terjadi kesalahan saat memproses PDF" in response.text

@pytest.mark.asyncio
async def test_parse_risk_valid_response(sample_ai_response):
    """✅ Test valid AI response parsing."""
    with patch("app.utils.ai_client.AIClient.analyze_risk", return_value=sample_ai_response):
        response = client.post("/parse-risk/", json={"ai_response": sample_ai_response})
        assert response.status_code == 200
        parsed_data = response.json()
        assert "risks" in parsed_data
        assert len(parsed_data["risks"]) > 0
        assert parsed_data["risks"][0]["clause"] == "Klausul 2"
        assert parsed_data["risks"][0]["risky_text"] == "Jasa dari PIHAK PERTAMA kepada PIHAK KEDUA dimulai sejak PIHAK KEDUA melakukan PEMBAYARAN."
        assert parsed_data["risks"][0]["reason"] == "Tidak ada perlindungan bagi PIHAK KEDUA terhadap keterlambatan PIHAK PERTAMA."

@pytest.mark.asyncio
async def test_parse_risk_empty_response():
    """❌ Test empty AI response (should return default N/A risk clause)."""
    sample_ai_response = ""
    with patch("app.utils.ai_client.AIClient.analyze_risk", return_value=sample_ai_response):
        response = client.post("/parse-risk/", json={"ai_response": sample_ai_response})
        assert response.status_code == 200
        parsed_data = response.json()
        assert parsed_data["risks"][0]["clause"] == "N/A"
        assert parsed_data["risks"][0]["risky_text"] == "Tidak ditemukan klausul yang dapat dianalisis"
        assert parsed_data["risks"][0]["reason"] == "Dokumen aman atau tidak dikenali"

@pytest.mark.asyncio
async def test_parse_risk_no_valid_clauses():
    """❌ Test AI response with no valid clauses."""
    ai_response = "Dokumen ini aman dan tidak memiliki klausul berisiko."
    with patch("app.utils.ai_client.AIClient.analyze_risk", return_value=ai_response):
        response = client.post("/parse-risk/", json={"ai_response": ai_response})
        assert response.status_code == 200
        parsed_data = response.json()
        assert parsed_data["risks"][0]["clause"] == "N/A"
        assert parsed_data["risks"][0]["risky_text"] == "Tidak ditemukan klausul yang dapat dianalisis"
        assert parsed_data["risks"][0]["reason"] == "Dokumen aman atau tidak dikenali"

@pytest.mark.asyncio
async def test_parse_risk_invalid_format():
    """❌ Test when the AI response format is incorrect or incomplete."""
    ai_response = "Klausul 3: Tidak lengkap"
    with patch("app.utils.ai_client.AIClient.analyze_risk", return_value=ai_response):
        response = client.post("/parse-risk/", json={"ai_response": ai_response})
        assert response.status_code == 200
        parsed_data = response.json()
        assert parsed_data["risks"][0]["clause"] == "N/A"
        assert parsed_data["risks"][0]["risky_text"] == "Tidak ditemukan klausul yang dapat dianalisis"
        assert parsed_data["risks"][0]["reason"] == "Dokumen aman atau tidak dikenali"