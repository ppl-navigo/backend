from pydantic import BaseModel, EmailStr
from typing import Optional, List

class DeepSeekRequest(BaseModel):
    system_prompt: str
    query: str
    temperature: Optional[float] = 0.7

class LegalDocumentFormRequest(BaseModel):
    judul: str
    tujuan: str
    pihak: List[str]
    mulai_kerja_sama: str
    akhir_kerja_sama: str
    hak_pihak: List[str]
    kewajiban_pihak: List[str]
    pemecah_masalah: str
    comment: Optional[str] = None
    author: EmailStr