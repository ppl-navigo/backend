from app.services.retrieval.retrieval_strategy import RetrievalStrategy
from sqlmodel import Session

class SparseRetrieval(RetrievalStrategy):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def retrieve(self, query: str):
        pass