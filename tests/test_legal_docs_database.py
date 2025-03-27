import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlmodel import Session
from uuid import UUID, uuid4
from datetime import date

from fastapi import FastAPI
from app.model.legal_docs_generator import LegalDocument
from app.routers.legal_docs_generator.databases import router, get_session

class TestLegalDocsDatabase:
    @pytest.fixture
    def mock_db_session(self):
        return MagicMock(spec=Session)

    @pytest.fixture
    def client(self, mock_db_session):
        app = FastAPI()
        app.include_router(router)
        
        def override_get_session():
            return mock_db_session
            
        app.dependency_overrides[get_session] = override_get_session
        return TestClient(app)

    def test_create_and_read_document(self, client, mock_db_session):
        # Mock UUID generation
        mock_doc = LegalDocument(
            title="Sample",
            prompt="Generate",
            content="This is a legal doc.",
            time=date(2025, 4, 1),
            author="tester"
        )

        # Mock session operations
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.side_effect = [mock_doc]

        # Mock UUID generation in the model
        payload = {
            "title": "Sample",
            "prompt": "Generate",
            "content": "This is a legal doc.",
            "time": date(2025, 4, 1).isoformat(),
            "author": "tester"
        }
        
        # Test create document
        response = client.post("/legal-docs-generator/documents/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["author"] == "tester"

        # Mock get all documents
        mock_db_session.exec.return_value.all.return_value = [mock_doc]
        response = client.get("/legal-docs-generator/documents/")
        assert response.status_code == 200
        assert len(response.json()) == 1

        # Mock get single document
        mock_db_session.get.return_value = mock_doc
        response = client.get(f"/legal-docs-generator/documents/{mock_doc.id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Sample"

        # Mock get documents by author
        mock_db_session.exec.return_value.all.return_value = [mock_doc]
        response = client.get("/legal-docs-generator/documents/author/tester")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_delete_document(self, client, mock_db_session):
        mock_doc = LegalDocument(
            title="To Delete",
            prompt="Delete me",
            content="Temporary doc.",
            time=date(2025, 4, 1),
            author="deleter"
        )

        # Mock document retrieval and deletion
        mock_db_session.get.return_value = mock_doc
        mock_db_session.delete.return_value = None
        mock_db_session.commit.return_value = None

        response = client.delete(f"/legal-docs-generator/documents/{mock_doc.id}")
        assert response.status_code == 200
        assert response.json() == {"message": "Deleted successfully"}

        # Mock document not found after deletion
        mock_db_session.get.return_value = None
        response = client.get(f"/legal-docs-generator/documents/{mock_doc.id}")
        assert response.status_code == 404

    def test_read_nonexistent_document(self, client, mock_db_session):
        mock_db_session.get.return_value = None
        nonexistent_id = uuid4()
        response = client.get(f"/legal-docs-generator/documents/{nonexistent_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Document not found"

    def test_delete_nonexistent_document(self, client, mock_db_session):
        mock_db_session.get.return_value = None
        nonexistent_id = uuid4()
        response = client.delete(f"/legal-docs-generator/documents/{nonexistent_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Document not found"

    def test_read_docs_by_nonexistent_author(self, client, mock_db_session):
        mock_db_session.exec.return_value.all.return_value = []
        response = client.get("/legal-docs-generator/documents/author/nonexistent_author")
        assert response.status_code == 200
        assert response.json() == []

    def test_multiple_documents_same_author(self, client, mock_db_session):
        author = "multi_author"
        mock_docs = []
        
        # Create 3 mock documents
        for i in range(3):
            mock_doc = LegalDocument(
                title=f"Doc {i}",
                prompt=f"Test {i}",
                content=f"Content {i}",
                time=date(2025, 4, 1),
                author=author
            )
            mock_docs.append(mock_doc)

            # Mock document creation
            mock_db_session.add.return_value = None
            mock_db_session.commit.return_value = None
            mock_db_session.refresh.side_effect = [mock_doc]

            payload = {
                "title": f"Doc {i}",
                "prompt": f"Test {i}",
                "content": f"Content {i}",
                "time": date(2025, 4, 1).isoformat(),
                "author": author
            }
            response = client.post("/legal-docs-generator/documents/", json=payload)
            assert response.status_code == 200

        # Mock getting documents by author
        mock_db_session.exec.return_value.all.return_value = mock_docs
        response = client.get(f"/legal-docs-generator/documents/author/{author}")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 3
        assert all(doc["author"] == author for doc in result)
        assert [doc["id"] for doc in result] == [str(doc.id) for doc in mock_docs]
