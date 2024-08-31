from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    email: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: str

class UserResponse(UserBase):
    id: str