from app.services.retrieval.RetrievalStrategy import RetrievalStrategy
from sqlmodel import Session
from app.config.settings import settings
from ollama import Client

class DenseRetrieval(RetrievalStrategy):
    def __init__(self, db_session: Session):
        self.ollama_client = Client(host=settings.OLLAMA_URL)
        super().__init__(db_session)

    def __embed_query(self, query: str) -> list[int]:
        pass

    def retrieve(self, query: str):
        pass