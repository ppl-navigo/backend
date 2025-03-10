from config.mongo import documents_collection
from bson import ObjectId
from datetime import datetime, timezone

async def find_document_by_text(filename: str, extracted_text: str):
    """Check if a document with the same filename and extracted text exists."""
    return await documents_collection.find_one({"filename": filename, "extracted_text": extracted_text})

async def insert_new_document(filename: str, extracted_text: str, ai_response: str, parsed_risks: list):
    """Insert a new document into MongoDB and return the inserted ID."""
    document_data = {
        "filename": filename,
        "uploaded_at": datetime.now(timezone.utc),
        "extracted_text": extracted_text,
        "ai_analysis": ai_response,
        "risk_analysis": parsed_risks
    }
    result = await documents_collection.insert_one(document_data)
    return str(result.inserted_id)

async def get_document_by_id(document_id: str):
    """Retrieve a document from MongoDB by its ID."""
    document = await documents_collection.find_one({"_id": ObjectId(document_id)})
    if document:
        document["_id"] = str(document["_id"])
    return document
