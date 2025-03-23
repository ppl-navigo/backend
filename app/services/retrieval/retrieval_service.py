from app.services.retrieval.retrieval_strategy import RetrievalStrategy
from app.services.retrieval.dense import DenseRetrieval
from app.services.retrieval.sparse import SparseRetrieval
from sqlmodel import Session
from typing import Annotated

class RetrievalService:
    def __init__(self, strategy: RetrievalStrategy):
        ...

    def retrieve(self, query: str):
        ...
    
class RetrievalServiceFactory:
    def __init__(self, method: str):
       ...

    def create(self, db: Session) -> RetrievalStrategy:
        ...
    
def get_retrieval_strategy(method: str):    
    ...

RetrievalDep = Annotated[RetrievalService, get_retrieval_strategy]