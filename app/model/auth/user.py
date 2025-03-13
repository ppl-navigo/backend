from pydantic import BaseModel

class User:
    def __init__(self, username: str, password: str, user_id: int = None, is_active: bool = True):
        self.id = user_id
        self.username = username
        self.password = password
        self.is_active = is_active

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True