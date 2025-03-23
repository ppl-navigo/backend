import pytest
from unittest.mock import Mock, patch
from app.services.retrieval.retrieval_service import RetrievalService, RetrievalServiceFactory, get_retrieval_strategy
from app.services.retrieval.retrieval_strategy import RetrievalStrategy
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

class TestGetRetrievalStrategy:
    @patch('app.services.retrieval.retrieval_service.RetrievalServiceFactory')
    def test_get_retrieval_strategy(self, mock_factory):
        # Arrange
        mock_factory.return_value.create.return_value = Mock(spec=RetrievalStrategy)
        
        # Act
        strategy_generator = get_retrieval_strategy("dense")
        retrieval_service = next(strategy_generator)
        
        # Assert
        mock_factory.assert_called_once_with("dense")
        mock_factory.return_value.create.assert_called_once()
        assert isinstance(retrieval_service, RetrievalService)

    def test_create_instantiates_correct_strategy(self):
        # Arrange
        mock_db = Mock(spec=Session)
        factory = RetrievalServiceFactory("dense")
        mock_dense = Mock()
        
        # Act
        with patch.dict(factory.strategies, {"dense": mock_dense}):
            result = factory.create(mock_db)
            
        # Assert
        mock_dense.assert_called_once_with(mock_db)
        assert result == mock_dense.return_value
    def test_create_with_sparse_method(self):
        # Arrange
        mock_db = Mock(spec=Session)
        factory = RetrievalServiceFactory("sparse")
        mock_sparse = Mock()
        
        # Act
        with patch.dict(factory.strategies, {"sparse": mock_sparse}):
            result = factory.create(mock_db)
            
        # Assert
        mock_sparse.assert_called_once_with(mock_db)
        assert result == mock_sparse.return_value
        assert result == mock_sparse.return_value

    def test_create_passes_db_to_strategy(self):
        # Arrange
        mock_db = Mock(spec=Session)
        factory = RetrievalServiceFactory("dense")
        mock_strategy = Mock()
        
        # Act
        with patch.dict(factory.strategies, {"dense": mock_strategy}):
            result = factory.create(mock_db)
            
        # Assert
        mock_strategy.assert_called_once_with(mock_db)
        assert result == mock_strategy.return_value
