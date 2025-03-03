from app.retriever.retrieval_strategy import RetrievalStrategy

class LegalDocRetrievalStrategy(RetrievalStrategy):
    def retrieve(self, embedding):
        return super().retrieve(embedding)
    
    def rerank(self, results):
        return super().rerank(results)