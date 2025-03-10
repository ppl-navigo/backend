import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.parsers import ParserFactory
from app.utils.ai_client import AIClient
from app.utils.risk_parser import RiskParser
from app.database.mongo import find_document_by_text, insert_new_document, get_document_by_id

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/analyze/")
async def analyze_document(file: UploadFile = File(...)):
    """Handles document analysis request."""
    file_extension = file.filename.split(".")[-1].lower()

    # Save file temporarily
    temp_file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    parser = ParserFactory.get_parser(file_extension)
    extracted_text = parser.extract_text(temp_file_path)

    # Cleanup temp file
    os.remove(temp_file_path)

    # **Check if document already exists in MongoDB**
    existing_document = await find_document_by_text(file.filename, extracted_text)

    if existing_document:
        return {
            "document_id": str(existing_document["_id"]),
            "risks": existing_document["risk_analysis"]
        }

    # If it's a new document, proceed with AI analysis
    ai_response = AIClient.analyze_risk(extracted_text)
    parsed_risks = RiskParser.parse_ai_risk_analysis(ai_response)

    # Save analysis result to MongoDB
    document_id = await insert_new_document(file.filename, extracted_text, ai_response, parsed_risks)

    return {"document_id": document_id, "risks": parsed_risks}

@router.get("/analysis/{document_id}")
async def get_analysis(document_id: str):
    """Retrieve an analyzed document from MongoDB."""
    document = await get_document_by_id(document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    return document
