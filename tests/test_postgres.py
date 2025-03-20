import pytest
from sqlmodel import SQLModel
from app.commons.db.postgres import Postgres
from fastapi import Depends
from sqlalchemy.orm import Session
from pydantic import Annotated

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