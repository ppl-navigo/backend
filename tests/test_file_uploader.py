import os
import shutil
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from fastapi.testclient import TestClient
from httpx import AsyncClient
from io import BytesIO
import fitz
from app.main import app
from app.routers.file_uploader import upload_document
from io import BytesIO
from fastapi import HTTPException, UploadFile
from app.main import app

client = TestClient(app)
UPLOAD_DIR = "uploads"

@pytest.fixture
def setup_upload_dir():
    """Ensure upload directory exists for tests"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    yield
    # Clean up any leftover files after tests
    for file in os.listdir(UPLOAD_DIR):
        try:
            os.remove(os.path.join(UPLOAD_DIR, file))
        except:
            pass

def create_valid_pdf():
    """Creates a minimal valid PDF in memory"""
    pdf_stream = BytesIO()
    doc = fitz.open()  # Create a blank PDF
    doc.new_page(width=595, height=842)  # Add a blank A4 page
    doc.save(pdf_stream)
    pdf_stream.seek(0)  # Move cursor to the beginning
    return pdf_stream

def create_valid_pdf_with_text():
    """Create a minimal PDF in memory with actual text so we confirm extraction."""
    pdf_stream = BytesIO()
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    # Insert some text
    page.insert_text((72, 72), "Hello, coverage!")
    doc.save(pdf_stream)
    pdf_stream.seek(0)
    return pdf_stream

@pytest.mark.asyncio
async def test_upload_valid_pdf():
    """Positive test: Upload a valid PDF under 10MB"""
    pdf_content = create_valid_pdf()
    files = {"file": ("test.pdf", pdf_content, "application/pdf")}
    response = client.post("/upload/", files=files, data={"prompt": "Test prompt"})
    
    assert response.status_code == 200
    assert "extracted_text" in response.json()
    assert "File processed successfully" in response.json()["message"]

@pytest.mark.asyncio
async def test_upload_non_pdf_file():
    """Negative test: Upload a non-PDF file"""
    txt_content = BytesIO(b"Just some text")
    files = {"file": ("test.txt", txt_content, "text/plain")}
    response = client.post("/upload/", files=files, data={"prompt": "Test prompt"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed"

@pytest.mark.asyncio
async def test_upload_uppercase_pdf():
    """Test uploading a file with uppercase PDF extension."""
    pdf_content = create_valid_pdf()
    files = {"file": ("TEST.PDF", pdf_content, "application/pdf")}  # Uppercase extension
    response = client.post("/upload/", files=files, data={"prompt": "Test prompt"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed"

@pytest.mark.asyncio
async def test_large_pdf_exception_direct():
    """Directly test that a PDF file exceeding the 10MB limit triggers the exception."""
    
    # Define a custom BytesIO subclass that simulates a large file.
    class FakeFile(BytesIO):
        def seek(self, offset, whence=0):
            return super().seek(offset, whence)
        def tell(self):
            # Return a size slightly larger than 10MB.
            return 10 * 1024 * 1024 + 1
    
    # Create an UploadFile with a valid PDF extension but with a fake file size.
    mock_file = UploadFile(file=FakeFile(b"%PDF-1.4"), filename="test.pdf")
    
    with pytest.raises(HTTPException) as excinfo:
        await upload_document(file=mock_file, prompt="dummy prompt")
    
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "File size exceeds 10MB limit"

@pytest.mark.asyncio
async def test_upload_empty_pdf():
    """Edge case: Upload an empty but valid PDF file"""
    valid_empty_pdf = create_valid_pdf()
    files = {"file": ("empty.pdf", valid_empty_pdf, "application/pdf")}
    response = client.post("/upload/", files=files, data={"prompt": "Test prompt"})

    assert response.status_code == 200
    assert response.json()["message"] == "File processed successfully"

@pytest.mark.asyncio
async def test_extract_text_pdf_failure():
    """Test failure in PDF text extraction due to a corrupt PDF."""
    corrupt_pdf_content = BytesIO(b"This is not a valid PDF file")
    files = {"file": ("corrupt.pdf", corrupt_pdf_content, "application/pdf")}

    response = client.post("/upload/", files=files, data={"prompt": "Test prompt"})

    assert response.status_code == 500
    assert "Error processing PDF" in response.json()["detail"]

@pytest.mark.asyncio
async def test_os_remove_failure():
    """Test failure in deleting the uploaded file after processing."""
    pdf_content = create_valid_pdf()
    files = {"file": ("delete_fail.pdf", pdf_content, "application/pdf")}
    
    with patch("os.remove", side_effect=Exception("File deletion error")):
        response = client.post("/upload/", files=files, data={"prompt": "Test prompt"})

    assert response.status_code == 500
    assert "File deletion error" in response.json()["detail"]

@pytest.mark.asyncio
async def test_file_save_failure():
    """Test failure in saving the uploaded file before processing."""
    pdf_content = create_valid_pdf()
    files = {"file": ("save_fail.pdf", pdf_content, "application/pdf")}

    with patch("builtins.open", mock_open()) as mocked_open:
        mocked_open.side_effect = IOError("File write error")
        response = client.post("/upload/", files=files, data={"prompt": "Test prompt"})

    assert response.status_code == 500
    assert "File write error" in response.json()["detail"]

@pytest.mark.asyncio
async def test_general_exception_handling():
    """Test handling of unexpected exceptions during the upload process."""
    pdf_content = create_valid_pdf()
    files = {"file": ("unexpected_error.pdf", pdf_content, "application/pdf")}

    with patch("app.routers.file_uploader.extract_text_pdf", side_effect=Exception("Unexpected Server Error")):
        response = client.post("/upload/", files=files, data={"prompt": "Test prompt"})

    assert response.status_code == 500
    assert "Unexpected Server Error" in response.json()["detail"]

@pytest.mark.asyncio
async def test_missing_prompt_parameter():
    """Test that omitting the 'prompt' Form parameter raises a 422."""
    pdf_content = create_valid_pdf()
    files = {"file": ("test.pdf", pdf_content, "application/pdf")}
    response = client.post("/upload/", files=files)

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_missing_file_parameter():
    """Test that omitting the 'file' parameter raises a 422."""
    response = client.post("/upload/", data={"prompt": "No file present"})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_upload_directory_creation(setup_upload_dir):
    """Test that the upload directory is created if it doesn't exist."""
    shutil.rmtree(UPLOAD_DIR, ignore_errors=True)  # Remove directory first
    
    assert not os.path.exists(UPLOAD_DIR), "Upload directory should NOT exist before test"

    pdf_content = create_valid_pdf()
    files = {"file": ("test.pdf", pdf_content, "application/pdf")}
    response = client.post("/upload/", files=files, data={"prompt": "Test prompt"})

    assert response.status_code == 200
    assert os.path.exists(UPLOAD_DIR), "Upload directory was not created"

@pytest.mark.asyncio
async def test_case_sensitive_pdf_extension(setup_upload_dir):
    """Test that PDF extension check is case sensitive."""
    pdf_content = create_valid_pdf()
    files = {"file": ("TEST.PDF", pdf_content, "application/pdf")}
    response = client.post("/upload/", files=files, data={"prompt": "Test"})
    
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_full_happy_path_no_mocks():
    """Test the entire happy path without any mocks."""
    shutil.rmtree(UPLOAD_DIR, ignore_errors=True)

    pdf_content = create_valid_pdf_with_text()
    files = {"file": ("example.pdf", pdf_content, "application/pdf")}

    response = client.post("/upload/", files=files, data={"prompt": "Just a test"})
    assert response.status_code == 200, response.text

    # Check if file was temporarily written before deletion
    temp_file_path = os.path.join(UPLOAD_DIR, "example.pdf")
    assert not os.path.exists(temp_file_path), "Temporary file should be deleted"

    data = response.json()
    assert data["message"] == "File processed successfully"
    assert data["prompt"] == "Just a test"
    assert "Hello, coverage!" in data["extracted_text"]

# Direct function tests
@pytest.mark.asyncio
async def test_upload_document_direct():
    """Test the upload_document function directly."""
    from fastapi import UploadFile
    from app.routers.file_uploader import upload_document

    # Create a mock file
    pdf_content = create_valid_pdf()
    mock_file = UploadFile(file=pdf_content, filename="test.pdf")

    # Call function directly
    result = await upload_document(file=mock_file, prompt="Test prompt")

    assert result["message"] == "File processed successfully"
    assert "extracted_text" in result
    assert result["prompt"] == "Test prompt"


@pytest.mark.asyncio
async def test_upload_document_direct_failure():
    """Test the upload_document function directly with a failure case."""
    from fastapi import UploadFile
    from app.routers.file_uploader import upload_document

    # Create a mock file with invalid content
    mock_file = UploadFile(file=BytesIO(b"Not a PDF"), filename="test.pdf")  # REMOVE content_type

    # Call function directly and expect an exception
    with pytest.raises(Exception):
        await upload_document(file=mock_file, prompt="Test prompt")

@pytest.mark.asyncio
async def test_non_pdf_exception_direct():
    """Directly test that a non-PDF file triggers the exception."""
    # Create an UploadFile with a .txt extension
    mock_file = UploadFile(file=BytesIO(b"dummy content"), filename="test.txt")
    
    with pytest.raises(HTTPException) as excinfo:
        await upload_document(file=mock_file, prompt="dummy prompt")
    
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Only PDF files are allowed"