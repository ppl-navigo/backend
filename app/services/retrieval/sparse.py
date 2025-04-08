from app.services.retrieval.retrieval_strategy import RetrievalStrategy
from sqlmodel import Session, text

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
        statement = text("""
            SELECT DISTINCT document_id, page_number, MAX(ts_rank_cd(full_text_search, to_tsquery(:lang, :ts_query))) AS rank
            FROM legal_document_pages
            WHERE full_text_search @@ to_tsquery(:lang, :ts_query)
            GROUP BY document_id, page_number
            ORDER BY rank DESC
            LIMIT 20;
        """)

        res = self.db_session.exec(statement, params={
            "lang": "indonesian",
            "ts_query": clean_query
        }).all()

        return [{"document_id": r[0], "page_number": r[1]} for r in res]

