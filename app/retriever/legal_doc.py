from app.retriever.retrieval_strategy import RetrievalStrategy

class LegalDocRetrievalStrategy(RetrievalStrategy):
    def retrieve(self, embedding):
        return super().retrieve(embedding)