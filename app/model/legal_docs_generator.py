from sqlmodel import SQLModel, Field
from datetime import date
import uuid
from uuid import UUID

class LegalDocument(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    title: str
    prompt: str
    content: str
    time: date
    author: str