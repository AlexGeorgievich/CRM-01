from pydantic import BaseModel, Field


class PageMeta(BaseModel):
    total: int
    skip: int
    limit: int


class Message(BaseModel):
    message: str


class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
