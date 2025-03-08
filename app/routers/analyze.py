import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.parsers import ParserFactory
from app.utils.ai_client import AIClient
from app.utils.risk_parser import RiskParser

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/analyze/")
async def analyze_document(file: UploadFile = File(...)):
    """Handles document analysis request."""
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="❌ Only PDF and DOCX files are supported.")

    # Save file temporarily
    temp_file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    parser = ParserFactory.get_parser(file_extension)
    extracted_text = parser.extract_text(temp_file_path)

    # Cleanup temp file
    os.remove(temp_file_path)

    if "❌" in extracted_text:
        raise HTTPException(status_code=500, detail="❌ Failed to extract text.")

    # ✅ **Fix: Catch AI Errors**
    try:
        ai_response = AIClient.analyze_risk(extracted_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ AI Analysis Failed: {str(e)}")

    parsed_risks = RiskParser.parse_ai_risk_analysis(ai_response)
    return {"risks": parsed_risks}
