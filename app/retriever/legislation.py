from app.retriever.retrieval_strategy import RetrievalStrategy

class LegislationRetrievalStrategy(RetrievalStrategy):
    def retrieve(self, embedding):
        return super().retrieve(embedding)