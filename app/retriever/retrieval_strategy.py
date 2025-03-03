from abc import ABC, abstractmethod

class RetrievalStrategy(ABC):
    @abstractmethod
    def retrieve(self, embedding: list[float]) -> list[dict]:
        pass

class Retriever:
    def __init__(self, retrieval_strategy: RetrievalStrategy):
        pass

    def __embed_query(self, query: str) -> list[float]:
        pass

    def set_retrieval_strategy(self, retrieval_strategy: RetrievalStrategy):
        pass

    def retrieve(self, embedding: list[float]) -> list[dict]:
        pass