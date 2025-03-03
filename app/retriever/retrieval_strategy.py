from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer

class RetrievalStrategy(ABC):
    @abstractmethod
    def retrieve(self, embedding: list[float]) -> list[dict]:
        pass

class Retriever:
    def __init__(self, retrieval_strategy: RetrievalStrategy):
        self.retrieval_strategy = retrieval_strategy
        self.embedding_model = SentenceTransformer('BAAI/bge-m3')

    def __embed_query(self, query: str) -> list[float]:
        return self.embedding_model.encode(query).tolist()

    def set_retrieval_strategy(self, retrieval_strategy: RetrievalStrategy):
        self.retrieval_strategy = retrieval_strategy

    def retrieve(self, query: str) -> list[dict]:
        embedding = self.__embed_query(query)
        if not query:
            raise ValueError("Query is empty")
        return self.retrieval_strategy.retrieve(embedding)