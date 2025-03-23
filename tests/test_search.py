import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.retrieval.retrieval_service import RetrievalService
from app.routers.retrieval.search import get_retrieval_strategy

client = TestClient(app)

@pytest.fixture
def mock_retrieval_service():
    mock_service = MagicMock(spec=RetrievalService)
    return mock_service

@patch("app.routers.retrieval.search.get_retrieval_strategy")
def test_search_endpoint_returns_retrieval_results(mock_get_strategy, mock_retrieval_service):
    # Setup
    expected_results = ["document1", "document2"]
    mock_retrieval_service.retrieve.return_value = expected_results
    mock_get_strategy.return_value = mock_retrieval_service
    
    # Execute
    response = client.get("/search?query=test query&method=sparse")
    
    # Assert
    assert response.status_code == 200

@patch("app.routers.retrieval.search.get_retrieval_strategy")
def test_search_endpoint_with_empty_query(mock_get_strategy, mock_retrieval_service):
    # Setup
    expected_results = []
    mock_retrieval_service.retrieve.return_value = expected_results
    mock_get_strategy.return_value = mock_retrieval_service
    
    # Execute
    response = client.get("/search?query=&method=sparse")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == expected_results

    @patch("app.routers.retrieval.search.RetrievalServiceFactory")
    @patch("app.routers.retrieval.search.RetrievalService")
    def test_get_retrieval_strategy(mock_retrieval_service_cls, mock_factory_cls):
        # Setup
        mock_db = MagicMock()
        mock_factory = MagicMock()
        mock_factory_cls.return_value = mock_factory
        mock_strategy = MagicMock()
        mock_factory.create.return_value = mock_strategy
        mock_retrieval_service = MagicMock()
        mock_retrieval_service_cls.return_value = mock_retrieval_service
        
        # Execute
        strategy_generator = get_retrieval_strategy("sparse", mock_db)
        strategy = next(strategy_generator)
        
        # Assert
        mock_factory_cls.assert_called_once_with("sparse")
        mock_factory.create.assert_called_once_with(mock_db)
        mock_retrieval_service_cls.assert_called_once_with(mock_strategy)
        assert strategy == mock_retrieval_service