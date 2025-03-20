from sqlmodel import SQLModel
from sqlmodel import Field, JSON
from typing import Optional, Any
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from datetime import date

class LegalDocument(SQLModel, table=True, arbitrary_types_allowed=True):
    id: str = Field(primary_key=True, index=True)
    title: Optional[str] = None
    jenis_bentuk_peraturan: Optional[str] = None
    pemrakarsa: Optional[str] = None
    nomor: Optional[str] = None
    tahun: Optional[int] = None
    tentang: Optional[str] = None
    tempat_penetapan: Optional[str] = None
    ditetapkan_tanggal: Optional[date] = None
    pejabat_yang_menetapkan: Optional[str] = None
    status: Optional[str] = None
    url: Optional[str] = None
    dasar_hukum: Optional[str] = Field(default_factory=list, sa_column=JSON)
    mengubah: Optional[str] = Field(default_factory=list, sa_column=JSON)
    diubah_oleh: Optional[str] = Field(default_factory=list, sa_column=JSON)
    mencabut: Optional[str] = Field(default_factory=list, sa_column=JSON)
    dicabut_oleh: Optional[str] = Field(default_factory=list, sa_column=JSON)
    melaksanakan_amanat_peraturan: Optional[str] = Field(default_factory=list, sa_column=JSON)
    dilaksanakan_oleh_peraturan_pelaksana: Optional[str] = Field(default_factory=list, sa_column=JSON)

class LegalDocumentChunk(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True)
    body: Optional[str] = None
    filename: Optional[str] = None
    last_modified: Optional[date] = None
    page_number: Optional[int] = None
    embedding: Any = Field(sa_type=Vector(1024))
    legal_document_id: Optional[str] = Field(foreign_key="legal_documents.id")


class LegalDocumentPage(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    document_id: str = Field(foreign_key="legal_documents.id")
    page_number: Optional[int] = None
    title: Optional[str] = None
    jenis_bentuk_peraturan: Optional[str] = None
    pemrakarsa: Optional[str] = None
    nomor: Optional[str] = None
    tahun: Optional[int] = None
    tentang: Optional[str] = None
    tempat_penetapan: Optional[str] = None
    ditetapkan_tanggal: Optional[date] = None
    pejabat_yang_menetapkan: Optional[str] = None
    status: Optional[str] = None
    url: Optional[str] = None
    dasar_hukum: Optional[str] = None
    mengubah: Optional[str] = None
    diubah_oleh: Optional[str] = None
    mencabut: Optional[str] = None
    dicabut_oleh: Optional[str] = None
    melaksanakan_amanat_peraturan: Optional[str] = None
    dilaksanakan_oleh_peraturan_pelaksana: Optional[str] = None
    combined_body: Optional[str] = None
    full_text_search: Optional[str] = None

