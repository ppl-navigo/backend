import pytest
from app.services.retrieval.DenseRetrieval import DenseRetrieval
from app.config.settings import settings

# Create a fake client to avoid external calls during testing.
class FakeClient:
    def __init__(self, host):
        self.host = host

# A dummy DB session for testing purposes.
class DummySession:
    def exec(self, *args, **kwargs):
        class FakeResult:
            def all(self):
                return []
        return FakeResult()

def test_init_sets_ollama_client(monkeypatch):
    # Patch the Client in SparseRetrieval to use FakeClient.
    monkeypatch.setattr("app.services.retrieval.DenseRetrieval.Client", FakeClient)
    dummy_session = DummySession()
    retriever = DenseRetrieval(dummy_session)
    
    # Verify that ollama_client is initialized with the correct host.
    assert isinstance(retriever.ollama_client, FakeClient)
    assert retriever.ollama_client.host == settings.OLLAMA_URL

def test_init_calls_parent(monkeypatch):
    # Patch the Client to avoid external dependency.
    monkeypatch.setattr("app.services.retrieval.DenseRetrieval.Client", FakeClient)
    dummy_session = DummySession()
    retriever = DenseRetrieval(dummy_session)
    
    # Assuming RetrievalStrategy.__init__ assigns db_session, verify it.
    assert hasattr(retriever, "db_session")
    assert retriever.db_session == dummy_session

def test_retrieve_calls_ollama(monkeypatch):
    # Patch the Client to avoid external dependency.
    monkeypatch.setattr("app.services.retrieval.DenseRetrieval.Client", FakeClient)
    
    # We don't need this since we're adding exec to DummySession class
    # def fake_execute(*args, **kwargs):
    #     return []
    # monkeypatch.setattr(DummySession, "exec", fake_execute)
    
    # Initialize the retriever
    dummy_session = DummySession()
    retriever = DenseRetrieval(dummy_session)
    
    # Mock the __embed_query method to avoid external calls.
    embed_called = False
    
    def fake_embed_query(query):
        nonlocal embed_called
        embed_called = True
        return [1, 2, 3]
    
    monkeypatch.setattr(retriever, "_DenseRetrieval__embed_query", fake_embed_query)

    # Call retrieve with a dummy query.
    retriever.retrieve("dummy query")
    
    # Verify that __embed_query was called
    assert embed_called
    assert retriever._DenseRetrieval__embed_query("dummy query") == [1, 2, 3]