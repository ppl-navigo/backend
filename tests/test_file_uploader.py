import pytest
import io
from unittest.mock import patch, MagicMock
from fastapi.datastructures import UploadFile
from fastapi import HTTPException

@pytest.mark.asyncio
@patch("app.routers.file_uploader.storage.Client")
async def test_upload_document_success(mock_storage_client):
    # Siapkan mock bucket & mock blob
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    # Panggilan storage.Client() -> mock_storage_client.return_value
    mock_storage_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    # Import di dalam function agar patch sudah aktif
    from app.routers.file_uploader import upload_document

    # Buat file PDF kecil
    file_content = b"%PDF-1.4 minimal pdf content"
    file_obj = io.BytesIO(file_content)
    file_obj.name = "test.pdf"

    upload_file = UploadFile(filename="test.pdf", file=file_obj)

    # Panggil fungsi
    result = await upload_document(upload_file)

    # Verifikasi
    assert result["message"] == "File uploaded successfully"
    assert result["file_path"].startswith("uploads/")
    assert result["saved_as"].endswith(".pdf")

    # Pastikan upload_from_file dipanggil persis sekali
    mock_blob.upload_from_file.assert_called_once()


@pytest.mark.asyncio
@patch("app.routers.file_uploader.storage.Client")
async def test_upload_document_not_pdf(mock_storage_client):
    from app.routers.file_uploader import upload_document

    file_content = b"some text"
    file_obj = io.BytesIO(file_content)
    file_obj.name = "test.txt"

    upload_file = UploadFile(filename="test.txt", file=file_obj)

    with pytest.raises(HTTPException) as excinfo:
        await upload_document(upload_file)

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Only PDF files are allowed"


@pytest.mark.asyncio
@patch("app.routers.file_uploader.storage.Client")
async def test_upload_document_too_large(mock_storage_client):
    from app.routers.file_uploader import upload_document

    # Buat file > 10MB
    file_content = b"x" * (10 * 1024 * 1024 + 1)
    file_obj = io.BytesIO(file_content)
    file_obj.name = "big.pdf"

    upload_file = UploadFile(filename="big.pdf", file=file_obj)

    with pytest.raises(HTTPException) as excinfo:
        await upload_document(upload_file)

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "File size exceeds 10MB limit"


@pytest.mark.asyncio
@patch("app.routers.file_uploader.storage.Client")
async def test_upload_document_gcs_exception(mock_storage_client):
    from app.routers.file_uploader import upload_document

    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    # Paksa upload_from_file melempar error
    mock_blob.upload_from_file.side_effect = Exception("Simulated GCS error")

    file_content = b"%PDF-1.4 minimal pdf content"
    file_obj = io.BytesIO(file_content)
    file_obj.name = "error.pdf"

    upload_file = UploadFile(filename="error.pdf", file=file_obj)

    with pytest.raises(HTTPException) as excinfo:
        await upload_document(upload_file)

    assert excinfo.value.status_code == 500
    assert "Simulated GCS error" in str(excinfo.value.detail)
