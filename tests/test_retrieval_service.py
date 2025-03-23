import pytest
from unittest.mock import Mock
from app.services.retrieval.retrieval_service import RetrievalService, RetrievalServiceFactory
from app.services.retrieval.retrieval_strategy import RetrievalStrategy
from app.services.retrieval.dense import DenseRetrieval
from app.services.retrieval.sparse import SparseRetrieval
from sqlmodel import Session

class TestRetrievalService:
    def test_retrieve_calls_strategy_retrieve(self):
        # Arrange
        mock_strategy = Mock(spec=RetrievalStrategy)
        mock_strategy.retrieve.return_value = ["result1", "result2"]
        service = RetrievalService(mock_strategy)
        service.strategy = mock_strategy  # Manually set strategy since __init__ sets it to None
        query = "test query"
        
        # Act
        result = service.retrieve(query)
        
        # Assert
        mock_strategy.retrieve.assert_called_once_with(query)
        assert result == ["result1", "result2"]

class TestRetrievalServiceFactory:
    def test_init_with_valid_method(self):
        # Act
        factory = RetrievalServiceFactory("dense")
        
        # Assert
        assert factory.method == "dense"
        
    def test_init_with_none_method(self):
        # Act/Assert
        with pytest.raises(ValueError, match="Method cannot be None"):
            RetrievalServiceFactory(None)
            
    def test_init_with_invalid_method(self):
        # Act/Assert
        with pytest.raises(ValueError, match="Invalid retrieval method"):
            RetrievalServiceFactory("invalid_method")

    def test_create_returns_correct_strategy(self):
        # Arrange
        factory = RetrievalServiceFactory("dense")
        mock_db = Mock(spec=Session)
        
        # Act
        strategy = factory.create(mock_db)
        
        # Assert
        assert isinstance(strategy, DenseRetrieval)
        
    def test_create_passes_db_to_strategy(self):
        # Arrange
        factory = RetrievalServiceFactory("sparse")
        mock_db = Mock(spec=Session)
        
        # Act
        strategy = factory.create(mock_db)
        
        # Assert
        assert isinstance(strategy, SparseRetrieval)
        # Verify the db was passed to the strategy constructor
        assert strategy.db_session == mock_db