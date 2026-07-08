from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.comment import CommentRead
from app.schemas.dictionary import CourseRead, SourceRead, StatusRead
from app.schemas.user import UserRead


class LeadBase(BaseModel):
    customer_name: str = Field(min_length=1, max_length=255)
    contact: str = Field(min_length=1, max_length=255)
    notes: str | None = None
    course_id: int | None = None
    source_id: int | None = None
    status_id: int
    assigned_manager_id: int | None = None
    next_contact_date: date | None = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    customer_name: str | None = Field(default=None, min_length=1, max_length=255)
    contact: str | None = Field(default=None, min_length=1, max_length=255)
    notes: str | None = None
    course_id: int | None = None
    source_id: int | None = None
    status_id: int | None = None
    assigned_manager_id: int | None = None
    next_contact_date: date | None = None


class LeadRead(LeadBase):
    id: int
    created_by_id: int | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime
    course: CourseRead | None = None
    source: SourceRead | None = None
    status: StatusRead
    assigned_manager: UserRead | None = None
    created_by: UserRead | None = None

    model_config = {"from_attributes": True}


class LeadDetail(LeadRead):
    comments: list[CommentRead] = Field(default_factory=list)


class LeadList(BaseModel):
    items: list[LeadRead]
    total: int
    skip: int
    limit: int
