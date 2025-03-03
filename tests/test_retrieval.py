from app.retriever.retrieval_strategy import Retriever
from app.retriever.legislation import LegislationRetrievalStrategy
from app.retriever.legal_doc import LegalDocRetrievalStrategy
from sentence_transformers import SentenceTransformer
from mock import Mock, patch
import numpy as np
import pytest

@pytest.fixture
def mock_legislation_retrieval_strategy():
    legal_doc_retrieval_strategy = Mock(spec=LegislationRetrievalStrategy)
    return legal_doc_retrieval_strategy

@pytest.fixture
def mock_legal_doc_retrieval_strategy():
    legal_doc_retrieval_strategy = Mock(spec=LegalDocRetrievalStrategy)
    return legal_doc_retrieval_strategy

@pytest.fixture
def mock_embedding_model():
    embedding_model = Mock(spec=SentenceTransformer)
    embedding_model.encode = lambda _: np.array([1, 2, 3])
    return embedding_model

def test_init_retriever():
    retriever = Retriever(LegislationRetrievalStrategy())
    assert retriever is not None

def test_set_retrieval_strategy(mock_legislation_retrieval_strategy, mock_legal_doc_retrieval_strategy):
    retriever = Retriever(LegislationRetrievalStrategy())
    retriever.set_retrieval_strategy(mock_legislation_retrieval_strategy)
    assert retriever.retrieval_strategy is mock_legislation_retrieval_strategy
    retriever.set_retrieval_strategy(mock_legal_doc_retrieval_strategy)
    assert retriever.retrieval_strategy is mock_legal_doc_retrieval_strategy

def test_retrieve_with_correct_embedding(mocker, mock_embedding_model):
    patch('sentence_transformers.SentenceTransformer', return_value=mock_embedding_model).start()
    patch('sentence_transformers.SentenceTransformer.encode', return_value=np.array([1, 2, 3])).start()
    strategy = LegislationRetrievalStrategy()
    mocker.patch.object(strategy, 'retrieve', return_value=[])
    retriever = Retriever(strategy)
    with patch.object(strategy, 'retrieve', return_value=[]):
        retriever.embedding_model = mock_embedding_model
        retriever.retrieve("lorem ipsum")
        strategy.retrieve.assert_called_once()

def test_retrieve_with_incorrect_embedding(mocker, mock_embedding_model):
    patch('sentence_transformers.SentenceTransformer', return_value=mock_embedding_model).start()  
    patch('sentence_transformers.SentenceTransformer.encode', return_value=np.array([1, 2, 3])).start()
    strategy = LegislationRetrievalStrategy()
    mocker.patch.object(strategy, 'retrieve', return_value=[])
    retriever = Retriever(strategy)
    with patch.object(strategy, 'retrieve', return_value=[]):
        with pytest.raises(ValueError):
            retriever.embedding_model = mock_embedding_model
            retriever.retrieve("")
        strategy.retrieve.assert_not_called()