from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.commons.db.postgres import Postgres
from app.services.retrieval.retrieval_service import RetrievalService, RetrievalServiceFactory
from app.config.settings import settings

postgres_db = Postgres(settings.DB_URL)
def get_retrieval_strategy(method: str, db: Session = Depends(postgres_db.get_session)):    
    yield RetrievalService(RetrievalServiceFactory(method).create(db))

router = APIRouter()

@router.get("/search")
async def search(query: str, retriever: RetrievalService = Depends(get_retrieval_strategy)):
    return retriever.retrieve(query)