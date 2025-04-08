import pytest
from sqlmodel import SQLModel, Session
from app.commons.db.postgres import Postgres

def test_default_url():
    # Test that when url is None, it uses the default memory SQLite URL
    pg = Postgres(None)
    
    # Verify the engine is created with the default URL
    assert 'sqlite:///:memory:' in str(pg.engine.url)
    assert pg.init is True

def test_create_db_and_tables_called(monkeypatch):
    call_args = []

    def fake_create_all(engine):
        call_args.append(engine)

    monkeypatch.setattr(SQLModel.metadata, "create_all", fake_create_all)

    # Instantiate Postgres; __create_db_and_tables is invoked during __init__
    pg = Postgres("sqlite:///:memory:")

    # Verify that create_all was invoked exactly once with the proper engine.
    assert len(call_args) == 1
    assert call_args[0] == pg.engine
    assert pg.init is True


def test_get_session(monkeypatch):
    # Mock the SQLModel.metadata.create_all to avoid actual table creation
    monkeypatch.setattr(SQLModel.metadata, "create_all", lambda _: None)
    
    # Create a test instance
    pg = Postgres("sqlite:///:memory:")
    
    # Create a test session for mocking
    test_session = Session(pg.engine)
    
    # Create a mock Session class
    original_init = Session.__init__
    def mock_session_init(*args, **kwargs):
        # Don't return anything from __init__
        original_init(*args, **kwargs)
        
    # Mock Session to return our test session when used as a context manager
    monkeypatch.setattr(Session, "__init__", mock_session_init)
    monkeypatch.setattr(Session, "__enter__", lambda _: test_session)
    monkeypatch.setattr(Session, "__exit__", lambda *args: None)
    
    # Get the session generator
    session_generator = pg.get_session()
    
    # Verify it yields the correct session
    session = next(session_generator)
    assert session == test_session
    
    # Verify generator is exhausted
    with pytest.raises(StopIteration):
        next(session_generator)
