from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, select
from datetime import date
from typing import List
from uuid import UUID, uuid4
from app.model.legal_docs_generator import LegalDocument
from app.config.settings import settings
from fastapi import APIRouter
from app.commons.db.postgres import Postgres

postgres_db = Postgres(settings.DB_URL)
PATH = "/legal-docs-generator"

def get_session():
    return next(postgres_db.get_session())  # use generator from Postgres

router = APIRouter()

@router.post(PATH + "/documents/", response_model=LegalDocument)
def create_doc(doc: LegalDocument, session: Session = Depends(get_session)):
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc

@router.get(PATH + "/documents/", response_model=List[LegalDocument])
def read_all_docs(session: Session = Depends(get_session)):
    return session.exec(select(LegalDocument)).all()

@router.get(PATH + "/documents/{doc_id}", response_model=LegalDocument)
def read_doc(doc_id: UUID, session: Session = Depends(get_session)):
    doc = session.get(LegalDocument, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get(PATH + "/documents/author/{author}", response_model=List[LegalDocument])
def read_docs_by_author(author: str, session: Session = Depends(get_session)):
    statement = select(LegalDocument).where(LegalDocument.author == author)
    return session.exec(statement).all()

@router.delete(PATH + "/documents/{doc_id}", response_model=dict)
def delete_doc(doc_id: UUID, session: Session = Depends(get_session)):
    doc = session.get(LegalDocument, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    session.delete(doc)
    session.commit()
    return {"message": "Deleted successfully"}