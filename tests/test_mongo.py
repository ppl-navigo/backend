import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from bson import ObjectId
from app.database.mongo import find_document_by_text, insert_new_document, get_document_by_id

# ✅ Ensure pytest doesn't close the event loop too soon
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_insert_and_find_document():
    """Test inserting and retrieving a document with full mocking (no real DB call)"""

    filename = "test_doc.txt"
    extracted_text = "This is a test document."
    ai_response = "Test AI Analysis"
    document_id = str(ObjectId())  # Generate a fake ID

    parsed_risks = [
        {"clause": "Klausul 1", "risky_text": "Example text", "reason": "Example reason"},
        {"clause": "Klausul 2", "risky_text": "Another risky text", "reason": "Another reason"}
    ]

    # ✅ Completely mock the MongoDB collection
    mock_collection = AsyncMock()
    mock_collection.insert_one.return_value.inserted_id = ObjectId(document_id)
    mock_collection.find_one.side_effect = lambda query: {
        "_id": ObjectId(document_id),
        "filename": filename,
        "uploaded_at": "mocked_date",
        "extracted_text": extracted_text,
        "ai_analysis": ai_response,
        "risk_analysis": parsed_risks
    } if query["_id"] == ObjectId(document_id) else None

    with patch("app.database.mongo.documents_collection", mock_collection):
        # ✅ Pretend to insert a document (doesn't actually insert)
        result_id = await insert_new_document(filename, extracted_text, ai_response, parsed_risks)
        assert result_id == document_id

        # ✅ Pretend to retrieve the document (mocked)
        retrieved_doc = await get_document_by_id(result_id)
        assert retrieved_doc is not None
        assert retrieved_doc["filename"] == filename
        assert retrieved_doc["extracted_text"] == extracted_text
        assert retrieved_doc["ai_analysis"] == ai_response

        # ✅ Validate risk analysis structure
        assert isinstance(retrieved_doc["risk_analysis"], list)
        assert len(retrieved_doc["risk_analysis"]) == 2
        assert "clause" in retrieved_doc["risk_analysis"][0]
        assert "risky_text" in retrieved_doc["risk_analysis"][0]
        assert "reason" in retrieved_doc["risk_analysis"][0]

@pytest.mark.asyncio
async def test_find_existing_document():
    """Test finding an existing document with full mocking"""

    filename = "existing_doc.txt"
    extracted_text = "Existing document content."
    ai_response = "Existing AI Analysis"
    document_id = str(ObjectId())

    parsed_risks = [
        {"clause": "Klausul A", "risky_text": "Sensitive data", "reason": "Potential GDPR violation"}
    ]

    # ✅ Mock the collection's find_one method to return a fake document
    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = {
        "_id": ObjectId(document_id),
        "filename": filename,
        "uploaded_at": "mocked_date",
        "extracted_text": extracted_text,
        "ai_analysis": ai_response,
        "risk_analysis": parsed_risks
    }

    with patch("app.database.mongo.documents_collection", mock_collection):
        existing_doc = await find_document_by_text(filename, extracted_text)

        assert existing_doc is not None
        assert existing_doc["filename"] == filename
        assert existing_doc["extracted_text"] == extracted_text

        # ✅ Validate risk analysis structure
        assert isinstance(existing_doc["risk_analysis"], list)
        assert len(existing_doc["risk_analysis"]) == 1
        assert "clause" in existing_doc["risk_analysis"][0]
        assert "risky_text" in existing_doc["risk_analysis"][0]
        assert "reason" in existing_doc["risk_analysis"][0]

@pytest.mark.asyncio
async def test_get_nonexistent_document():
    """Test retrieving a non-existent document with full mocking"""

    document_id = str(ObjectId())  # Generate a random ObjectId

    # ✅ Mock the database response to return None (document doesn't exist)
    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = None  # Simulate no result found

    with patch("app.database.mongo.documents_collection", mock_collection):
        # ✅ This doesn't actually query MongoDB, it just returns None
        document = await get_document_by_id(document_id)

        assert document is None  # Should return None
