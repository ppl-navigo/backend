import os
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from app.utils.pdf_parser import extract_text_pdf
import traceback

router = APIRouter()
UPLOAD_DIR = "uploads"  # Folder to store uploaded files
MAX_FILE_SIZE = 10 * 1024 * 1024  # Max file size = 10MB

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/")
async def upload_document(file: UploadFile = File(...), prompt: str = Form(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file.file.seek(0, 2)  # Move to end of file to get its size
    file_size = file.file.tell()
    file.file.seek(0)  # Reset cursor

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        # Save the uploaded file to disk
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Extract text using file path
        extracted_text = extract_text_pdf(file_path)

        # Delete the file after processing
        os.remove(file_path)
        
    except Exception as e:
        print("Error Traceback:", traceback.format_exc())  # Prints full error traceback
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "File processed successfully",
        "extracted_text": extracted_text,
        "prompt": prompt
    }


