from datetime import datetime

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: str | None = Field(default=None, max_length=255)
    full_name: str = Field(min_length=1, max_length=255)
    role: str = "manager"
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
