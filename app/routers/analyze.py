import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.parsers import ParserFactory
from app.utils.ai_client import AIClient
from app.utils.risk_parser import RiskParser

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.post("/extract_text/")
async def extract_text_from_document(file: UploadFile = File(...)):
    """Handles document text extraction request."""
    file_extension = file.filename.split(".")[-1].lower()

    # Save file temporarily
    temp_file_path = file.filename
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    parser = ParserFactory.get_parser(file_extension)
    # extracted_text = parser.extract_text(temp_file_path)
    pages_text = parser.extract_text(temp_file_path)

    # Cleanup temp file
    os.remove(temp_file_path)

    # return {"extracted_text": extracted_text}
    print(pages_text)
    return { "pages_text": pages_text }

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

    ai_response = AIClient.analyze_risk(extracted_text)

    parsed_risks = RiskParser.parse_ai_risk_analysis(ai_response)
    return {
            "extracted_text": extracted_text,  # Original text extracted from the document
            "ai_response": ai_response,  # The raw AI response for transparency
            "risks": parsed_risks  # The parsed risks from the AI response
        }