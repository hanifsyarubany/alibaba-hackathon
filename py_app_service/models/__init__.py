from pydantic import BaseModel
from typing import Optional, Union


class UserBase(BaseModel):
    email: str
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    id: str


class UserResponse(UserBase):
    id: str


class OnboardCreate(BaseModel):
    business_id: str
    data: dict


class OnboardModel(OnboardCreate):
    created_at: Union[int, float]
    success: Optional[bool] = None
    failed: Optional[bool] = None
    overview: Optional[dict] = None
    gtm: Optional[dict] = None
    market_opportunity: Optional[dict] = None
    funding_community: Optional[dict] = None


class ChatbotModel(BaseModel):
    question: str
