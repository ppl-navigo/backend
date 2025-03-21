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
        # Mock the query result
        mock_result = [
            MagicMock(page_number=1, document_id=1, similarity=0.8),
            MagicMock(page_number=2, document_id=1, similarity=0.7)
        ]
        mock_db_session.exec.return_value.all.return_value = mock_result
        
        # Test with a valid query
        result = sparse_retrieval.retrieve("legal document search")
        
        # Assert the result
        assert result == mock_result
        
        # Verify select was called with appropriate parameters
        mock_db_session.exec.assert_called_once()

    def test_retrieve_empty_query(self, sparse_retrieval, mock_db_session):
        # Test with an empty query
        result = sparse_retrieval.retrieve("")
        
        # Assert the result is an empty list
        assert result == []
        
        # Verify select was not called
        mock_db_session.exec.assert_not_called
    
    @patch('app.services.retrieval.sparse.select')
    @patch('app.services.retrieval.sparse.func')
    @patch('app.services.retrieval.sparse.text')
    def test_query_construction(self, mock_text, mock_func, mock_select, sparse_retrieval, mock_db_session):
        # Arrange
        mock_select.return_value.join.return_value.where.return_value.group_by.return_value.order_by.return_value.limit.return_value = "query"
        mock_func.to_tsquery.return_value = "tsquery"
        mock_func.ts_rank_cd.return_value.label.return_value = "rank"
        mock_text.return_value = "order"
        
        # Act
        sparse_retrieval.retrieve("legal document search")
        
        # Assert - verify the query was built correctly
        mock_select.assert_called_once()
        mock_func.to_tsquery.assert_any_call('english', 'legal & document & search')
        mock_func.to_tsquery.assert_any_call('indonesian', 'legal & document & search')
        mock_text.assert_called_once_with("similarity DESC")
        mock_db_session.exec.assert_called_once_with("query")