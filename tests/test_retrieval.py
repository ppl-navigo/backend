from app.retriever.retrieval_strategy import Retriever
from app.retriever.legislation import LegislationRetrievalStrategy
from app.retriever.legal_doc import LegalDocRetrievalStrategy
from mock import Mock
import pytest

@pytest.fixture
def mock_legislation_retrieval_strategy():
    legal_doc_retrieval_strategy = Mock(spec=LegislationRetrievalStrategy)
    return legal_doc_retrieval_strategy

@pytest.fixture
def mock_legal_doc_retrieval_strategy():
    legal_doc_retrieval_strategy = Mock(spec=LegalDocRetrievalStrategy)
    return legal_doc_retrieval_strategy

def test_init_retriever():
    retriever = Retriever(LegislationRetrievalStrategy())
    assert retriever is not None

def test_set_retrieval_strategy(mock_legislation_retrieval_strategy, mock_legal_doc_retrieval_strategy):
    retriever = Retriever(LegislationRetrievalStrategy())
    retriever.set_retrieval_strategy(mock_legislation_retrieval_strategy)
    assert retriever.retrieval_strategy is mock_legislation_retrieval_strategy
    retriever.set_retrieval_strategy(mock_legal_doc_retrieval_strategy)
    assert retriever.retrieval_strategy is mock_legal_doc_retrieval_strategy

def test_retrieve_with_correct_embedding(mocker):
    strategy = LegislationRetrievalStrategy()
    mocker.patch.object(strategy, 'retrieve', return_value=[])
    retriever = Retriever(strategy)
    retriever.retrieve([i for i in range(1024)])
    strategy.retrieve.assert_called_once()

def test_retrieve_with_incorrect_embedding(mocker):
    strategy = LegislationRetrievalStrategy()
    mocker.patch.object(strategy, 'retrieve', return_value=[])
    retriever = Retriever(strategy)
    with pytest.raises(ValueError):
        retriever.retrieve([i for i in range(1023)])
    strategy.retrieve.assert_not_called()

def test_retrieve_with_no_embedding(mocker):
    strategy = LegislationRetrievalStrategy()
    mocker.patch.object(strategy, 'retrieve', return_value=[])
    retriever = Retriever(strategy)
    with pytest.raises(ValueError):
        retriever.retrieve(None)
    strategy.retrieve.assert_not_called()
