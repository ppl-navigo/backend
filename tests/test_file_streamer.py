import pytest
import urllib.parse
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from starlette.responses import StreamingResponse

from app.routers.file_streamer import router, stream_document

@pytest.mark.asyncio
@patch("app.routers.file_streamer.storage.Client")
async def test_stream_document_success(mock_storage_client):
    """
    Test sukses dengan memanggil stream_document() langsung.
    """
    # Siapkan mock bucket & blob
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    
    # Set agar get_bucket() -> mock_bucket
    mock_storage_client.return_value.bucket.return_value = mock_bucket
    # Ketika memanggil bucket.blob(...), kembalikan mock_blob
    mock_bucket.blob.return_value = mock_blob

    file_path = "documents/test.pdf"                
    decoded_path = urllib.parse.unquote(file_path)

    # Simulasikan isi file PDF (bisa apa saja, karena kita tdk cek .body_iterator)
    mock_blob.download_as_bytes.return_value = b"%PDF-1.4 minimal pdf content"

    # Pastikan file_path terdaftar di list_blobs agar tidak 404
    mock_blob_in_list = MagicMock()
    mock_blob_in_list.name = file_path
    mock_bucket.list_blobs.return_value = [mock_blob_in_list]

    # Panggil fungsi secara langsung
    response = await stream_document(decoded_path)

    # Verifikasi
    assert isinstance(response, StreamingResponse)
    assert response.status_code == 200
    assert response.media_type == "application/pdf"
    # Content-Disposition => inline
    assert response.headers["Content-Disposition"] == "inline; filename=test.pdf"

@pytest.mark.asyncio
@patch("app.routers.file_streamer.storage.Client")
async def test_stream_document_not_found(mock_storage_client):
    """
    Test gagal karena file tidak ditemukan di GCS.
    """
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    
    mock_storage_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    file_path = "documents/missing.pdf"
    decoded_path = urllib.parse.unquote(file_path)

    # Misal, di bucket hanya ada "documents/existing.pdf"
    mock_blob_in_list = MagicMock()
    mock_blob_in_list.name = "documents/existing.pdf"
    mock_bucket.list_blobs.return_value = [mock_blob_in_list]

    with pytest.raises(HTTPException) as excinfo:
        await stream_document(decoded_path)

    assert excinfo.value.status_code == 404
    assert "File not found in GCS" in excinfo.value.detail


@pytest.mark.asyncio
@patch("app.routers.file_streamer.storage.Client")
async def test_stream_document_gcs_exception(mock_storage_client):
    """
    Test gagal karena exception saat download dari GCS.
    """
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    
    mock_storage_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    file_path = "documents/error.pdf"
    decoded_path = urllib.parse.unquote(file_path)

    # Simulasikan file terdaftar di bucket -> agar lolos cek 404
    mock_blob_in_list = MagicMock()
    mock_blob_in_list.name = file_path
    mock_bucket.list_blobs.return_value = [mock_blob_in_list]

    # download_as_bytes melempar Exception => 500
    mock_blob.download_as_bytes.side_effect = Exception("Simulated GCS error")

    with pytest.raises(HTTPException) as excinfo:
        await stream_document(decoded_path)

    assert excinfo.value.status_code == 500
    assert "Failed to download PDF from GCS" in excinfo.value.detail