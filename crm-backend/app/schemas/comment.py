from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.user import UserRead


class CommentCreate(BaseModel):
    body: str = Field(min_length=1)


class CommentRead(BaseModel):
    id: int
    lead_id: int
    author_id: int | None
    body: str
    is_system: bool
    created_at: datetime
    updated_at: datetime
    author: UserRead | None = None

    model_config = {"from_attributes": True}
