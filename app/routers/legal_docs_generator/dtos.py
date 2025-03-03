from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List

class DeepSeekRequest(BaseModel):
    system_prompt: str = Field(..., description="System prompt to the model")
    query: str = Field(..., description="User query to the model")
    temperature: float = Field(0.7, description="Temperature of the model")

    @field_validator("system_prompt")
    def check_system_prompt(cls, value):
        if not value.strip():
            raise ValueError("System prompt field required")
        return value
    
    @field_validator("temperature")
    def check_temperature(cls, value):
        if value < 0 or value > 1:
            raise ValueError("Temperature value is not a valid float, must be between 0 and 1")

class LegalDocumentFormRequest(BaseModel):
    judul: str = Field(..., description="Judul is required and cannot be empty")
    tujuan: str = Field(..., description="Tujuan is required and cannot be empty")
    pihak: List[str] = Field(..., description="At least one pihak is required")
    mulai_kerja_sama: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Must be in YYYY-MM-DD format")
    akhir_kerja_sama: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Must be in YYYY-MM-DD format")
    hak_pihak: List[str] = Field(..., description="At least one hak_pihak is required")
    kewajiban_pihak: List[str] = Field(..., description="At least one kewajiban_pihak is required")
    pemecah_masalah: str = Field(..., description="Pemecah masalah is required and cannot be empty")
    comment: Optional[str] = None
    author: EmailStr = Field(..., description="Must be a valid email address")