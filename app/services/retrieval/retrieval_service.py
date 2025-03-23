from app.services.retrieval.retrieval_strategy import RetrievalStrategy
from app.services.retrieval.dense import DenseRetrieval
from app.services.retrieval.sparse import SparseRetrieval
from sqlmodel import Session
from typing import Annotated

class RetrievalService:
    def __init__(self, strategy: RetrievalStrategy):
        self.strategy: RetrievalStrategy = strategy

    def retrieve(self, query: str):
        return self.strategy.retrieve(query)
    
class RetrievalServiceFactory:
    def __init__(self, method: str):
        self.strategies = {
            "dense": DenseRetrieval,
            "sparse": SparseRetrieval,
        }
        if method is None:
            raise ValueError("Method cannot be None")
        if method not in self.strategies:
            raise ValueError(f"Invalid retrieval method: {method}, must be one of {list(self.strategies.keys())}")
        self.method = method

    def create(self, db: Session) -> RetrievalStrategy:
        strategy_class = self.strategies[self.method]
        return strategy_class(db)
    
def get_retrieval_strategy(method: str):    
    yield RetrievalService(RetrievalServiceFactory(method).create())

RetrievalDep = Annotated[RetrievalService, get_retrieval_strategy]