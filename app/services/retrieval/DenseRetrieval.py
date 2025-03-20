from app.services.retrieval.RetrievalStrategy import RetrievalStrategy
from app.model.chatbot.legal_document import LegalDocumentChunk, LegalDocument
from sqlmodel import Session
from sqlalchemy.sql import func
from app.config.settings import settings
from sqlmodel import select
from ollama import Client

class DenseRetrieval(RetrievalStrategy):
    def __init__(self, db_session: Session):
        self.ollama_client = Client(host=settings.OLLAMA_URL)
        super().__init__(db_session)

    def __embed_query(self, query: str) -> list[int]:
        return self.ollama_client.embed(model='bge-m3', input=query)[0]

    def retrieve(self, query: str):
        doc_embedding = self.__embed_query(query)
        similarity_expr = 1 - (LegalDocumentChunk.embedding.op('<=>')(doc_embedding))
        statement = (
            select(
                LegalDocumentChunk.page_number,
                LegalDocumentChunk.legal_document_id,
                func.max(similarity_expr).label("similarity")
            )
            .join(LegalDocument, LegalDocument.id == LegalDocumentChunk.legal_document_id)
            .where(
                LegalDocumentChunk.embedding.is_not(None),
                similarity_expr > 0.5
            )
            .group_by(LegalDocumentChunk.page_number, LegalDocumentChunk.legal_document_id)
            .order_by(func.max(similarity_expr).desc())
            .limit(20)
        )
        return self.db_session.exec(statement).all()
