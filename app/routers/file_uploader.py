import datetime
import logging
import traceback
from fastapi import APIRouter, File, UploadFile, HTTPException
from google.cloud import storage

router = APIRouter()

BUCKET_NAME = "mou-pdf"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    """Uploads a PDF to GCS and saves it permanently."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    file_name = os.path.splitext(file.filename)[0]
    unique_filename = f"{file_name}_{timestamp}{file_extension}"
    gcs_file_path = f"uploads/{unique_filename}"

    # Create fresh clients/buckets each call (so the patch will work):
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)

    try:
        blob = bucket.blob(gcs_file_path)
        blob.upload_from_file(file.file, content_type="application/pdf")

    except Exception as e:
        logging.error("Error Traceback: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "File uploaded successfully",
        "file_path": gcs_file_path,
        "saved_as": unique_filename
    }
