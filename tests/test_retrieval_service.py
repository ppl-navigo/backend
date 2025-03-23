import pytest
from unittest.mock import Mock
from app.services.retrieval.retrieval_service import RetrievalService, RetrievalServiceFactory
from app.services.retrieval.retrieval_strategy import RetrievalStrategy

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