import urllib.parse
import logging
import traceback
from fastapi import APIRouter, HTTPException
from google.cloud import storage
from starlette.responses import StreamingResponse
import os

router = APIRouter()
BUCKET_NAME = "mou-pdf"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

def get_bucket():
    """Returns a mockable GCS bucket instance."""
    client = storage.Client()
    return client.bucket(BUCKET_NAME)

# Ini dipanggil saat modul diimpor
bucket = get_bucket()

@router.get("/download/{filename:path}")
async def download_document(filename: str):
    """Downloads a PDF file directly from Google Cloud Storage."""
    decoded_filename = urllib.parse.unquote(filename).strip()
    gcs_file_path = decoded_filename

    # Print available files (for debugging)
    blobs = list(bucket.list_blobs())
    available_files = [blob.name for blob in blobs]
    print("📌 Available files in GCS:", available_files)

    if gcs_file_path not in available_files:
        print(f"❌ File {gcs_file_path} NOT FOUND in GCS")
        raise HTTPException(status_code=404, detail="File not found in GCS")

    blob = bucket.blob(gcs_file_path)

    try:
        pdf_bytes = blob.download_as_bytes()
    except Exception:
        logging.error("Error Traceback: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to download PDF from GCS")

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={decoded_filename.split('/')[-1]}"}
    )