from app.services.retrieval.retrieval_strategy import RetrievalStrategy
from app.model.chatbot.legal_document import LegalDocumentPage, LegalDocument
from sqlmodel import Session
from sqlalchemy.sql import func, text
from sqlmodel import select

class SparseRetrieval(RetrievalStrategy):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def retrieve(self, query: str):
        # Clean and prepare the query for PostgreSQL ts_query
        # Remove special characters and convert to ts_query format
        clean_query = ' & '.join(word for word in query.split() if len(word) > 2)
        
        if not clean_query:
            return []
            
        # Use PostgreSQL's ts_rank to score documents against the query using the indexed tsvector
        statement = (
            select(
                LegalDocumentPage.page_number,
                LegalDocumentPage.document_id,
                func.ts_rank_cd(
                    LegalDocumentPage.full_text_search, 
                    func.to_tsquery('english', clean_query)
                ).label("similarity")
            )
            .join(LegalDocument, LegalDocument.id == LegalDocumentPage.document_id)
            .where(
                LegalDocumentPage.full_text_search.op('@@')(func.to_tsquery('indonesian', clean_query))
            )
            .group_by(LegalDocumentPage.page_number, LegalDocumentPage.document_id, "similarity")
            .order_by(text("similarity DESC"))
            .limit(20)
        )
        return self.db_session.exec(statement).all()
