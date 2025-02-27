from pydantic import BaseModel, EmailStr
from typing import Optional, List

class DeepSeekRequest(BaseModel):
    system_prompt: str
    query: str
    temperature: Optional[float] = 0.7