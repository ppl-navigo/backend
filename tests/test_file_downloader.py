import pytest
import urllib.parse
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from starlette.responses import StreamingResponse

# 1) Patch google.cloud.storage.Client sebelum import file_downloader
mock_storage_client = MagicMock()
with patch("google.cloud.storage.Client", return_value=mock_storage_client):
    from app.routers.file_downloader import download_document
    import app.routers.file_downloader as fd  # agar kita bisa timpa fd.bucket

@pytest.mark.asyncio
async def test_download_document_success():
    """
    Test sukses (file ada, download_as_bytes() berhasil) -> 200
    """
    # 2) Siapkan mock bucket & mock blob
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    # 3) Timpa bucket global di file_downloader
    fd.bucket = mock_bucket

    file_path = "documents/test.pdf"
    decoded_path = urllib.parse.unquote(file_path)

    # 4) Daftar file agar tidak 404
    mock_blob_in_list = MagicMock()
    mock_blob_in_list.name = file_path
    mock_bucket.list_blobs.return_value = [mock_blob_in_list]

    # 5) Pastikan bucket.blob(...) -> mock_blob
    mock_bucket.blob.return_value = mock_blob

    # 6) Simulasi hasil download
    mock_blob.download_as_bytes.return_value = b"%PDF-1.4 minimal pdf content"

    # 7) Panggil fungsi
    response = await download_document(decoded_path)

    # 8) Verifikasi
    assert isinstance(response, StreamingResponse)
    assert response.status_code == 200
    assert response.media_type == "application/pdf"
    assert response.headers["Content-Disposition"] == "attachment; filename=test.pdf"


@pytest.mark.asyncio
async def test_download_document_not_found():
    """
    Test 404 (file tidak ada di bucket)
    """
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    # Timpa bucket global
    fd.bucket = mock_bucket

    file_path = "documents/missing.pdf"
    decoded_path = urllib.parse.unquote(file_path)

    # Di bucket hanya ada file lain -> memicu 404
    mock_blob_in_list = MagicMock()
    mock_blob_in_list.name = "documents/another.pdf"
    mock_bucket.list_blobs.return_value = [mock_blob_in_list]

    mock_bucket.blob.return_value = mock_blob

    with pytest.raises(HTTPException) as excinfo:
        await download_document(decoded_path)

    assert excinfo.value.status_code == 404
    assert "File not found in GCS" in excinfo.value.detail


@pytest.mark.asyncio
async def test_download_document_gcs_exception():
    """
    Test 500 (file ada, tapi error download)
    """
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    # Timpa bucket
    fd.bucket = mock_bucket

    file_path = "documents/error.pdf"
    decoded_path = urllib.parse.unquote(file_path)

    # File terdaftar
    mock_blob_in_list = MagicMock()
    mock_blob_in_list.name = file_path
    mock_bucket.list_blobs.return_value = [mock_blob_in_list]

    mock_bucket.blob.return_value = mock_blob
    # Munculkan error
    mock_blob.download_as_bytes.side_effect = Exception("Simulated GCS error")

    with pytest.raises(HTTPException) as excinfo:
        await download_document(decoded_path)

    assert excinfo.value.status_code == 500
    assert "Failed to download PDF from GCS" in excinfo.value.detail
