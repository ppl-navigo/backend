import pytest
from unittest.mock import MagicMock, patch
from app.services.retrieval.sparse import SparseRetrieval
from sqlmodel import Session

class TestSparseRetrieval:
    
    @pytest.fixture
    def mock_db_session(self):
        return MagicMock(spec=Session)
    
    @pytest.fixture
    def sparse_retrieval(self, mock_db_session):
        return SparseRetrieval(mock_db_session)
    
    def test_retrieve_valid_query(self, sparse_retrieval, mock_db_session):
        # Mock the query result - the actual result is a list of tuples with (document_id, page_number, rank)
        mock_result = [
            (1, 1, 0.8),
            (1, 2, 0.7)
        ]
        mock_db_session.exec.return_value.all.return_value = mock_result
        
        # Test with a valid query
        result = sparse_retrieval.retrieve("legal document search")
        
        # Assert the result - now it's a list of dicts with document_id and page_number
        expected_result = [
            {"document_id": 1, "page_number": 1},
            {"document_id": 1, "page_number": 2}
        ]
        assert result == expected_result
        
        # Verify exec was called with appropriate parameters
        mock_db_session.exec.assert_called_once()

    def test_retrieve_empty_query(self, sparse_retrieval, mock_db_session):
        # Test with an empty query
        result = sparse_retrieval.retrieve("")
        
        # Assert the result is an empty list
        assert result == []
    @patch('app.services.retrieval.sparse.text')
    def test_query_construction(self, mock_text, sparse_retrieval, mock_db_session):
        # Arrange
        mock_text.return_value = "sql_query"
        mock_db_session.exec.return_value.all.return_value = []
        
        # Act
        sparse_retrieval.retrieve("legal document search")
        
        # Assert - verify the query was built correctly
        mock_text.assert_called_once()
        # Verify params were passed correctly
        mock_db_session.exec.assert_called_once_with("sql_query", params={
            "lang": "indonesian",
            "ts_query": "legal & document & search"
        })