import urllib.parse
import logging
import traceback
from fastapi import APIRouter, HTTPException
from google.cloud import storage
from starlette.responses import StreamingResponse

router = APIRouter()
BUCKET_NAME = "mou-pdf"

def get_bucket():
    # Buat Client & Bucket baru setiap kali (agar mudah di-mock dalam testing)
    client = storage.Client()
    return client.bucket(BUCKET_NAME)

@router.get("/stream/{filename:path}")
async def stream_document(filename: str):
    """Downloads a PDF file directly from Google Cloud Storage."""
    bucket = get_bucket()

    decoded_filename = urllib.parse.unquote(filename).strip()
    gcs_file_path = decoded_filename

    # Daftar semua blob di bucket -> cek apakah file terdaftar
    blobs = list(bucket.list_blobs())
    available_files = [blob.name for blob in blobs]
    # print("📌 Available files in GCS:", available_files)

    if gcs_file_path not in available_files:
        print(f"❌ File {gcs_file_path} NOT FOUND in GCS")
        raise HTTPException(status_code=404, detail="File not found in GCS")

    blob = bucket.blob(gcs_file_path)
    try:
        pdf_bytes = blob.download_as_bytes()
    except Exception:
        # Perbaiki logging agar tidak error
        logging.error("Traceback: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to download PDF from GCS")

    # Kembalikan PDF dengan 'inline' agar browser menampilkannya
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={decoded_filename.split('/')[-1]}"}
    )