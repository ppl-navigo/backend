from app.services.retrieval.retrieval_strategy import RetrievalStrategy
from sqlmodel import Session
from app.config.settings import settings
from sqlmodel import text
from ollama import Client

class DenseRetrieval(RetrievalStrategy):
    def __init__(self, db_session: Session):
        self.ollama_client = Client(host=settings.OLLAMA_URL)
        super().__init__(db_session)

    def __embed_query(self, query: str) -> list[int]:
        return self.ollama_client.embed(model='bge-m3', input=query).embeddings[0]

    def retrieve(self, query: str):
        doc_embedding = self.__embed_query(query)
        statement = (
            text("""
            SELECT chunk.page_number, chunk.legal_document_id,
            MAX((1 - (chunk.embedding <=> CAST(:query_embedding AS vector)))) AS similarity
            FROM legal_document_chunks AS chunk
            JOIN legal_documents AS doc ON doc.id = chunk.legal_document_id
            WHERE chunk.embedding IS NOT NULL AND (1 - (chunk.embedding <=> CAST(:query_embedding AS vector))) > 0.5
            GROUP BY chunk.page_number, chunk.legal_document_id
            ORDER BY similarity DESC
            LIMIT 20;
            """)
        )
        res = self.db_session.exec(statement, params={
            "query_embedding": doc_embedding,
        }).all()

        return [{"document_id": r[1], "page_number": r[0]} for r in res]
        
