from abc import ABC, abstractmethod
from dataclasses import dataclass
from sqlmodel import Session

@dataclass
class DocumentRef:
    document_id: str
    page_number: int

class RetrievalStrategy(ABC):
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    @abstractmethod
    def retrieve(self, query: str) -> list[DocumentRef]:
        pass