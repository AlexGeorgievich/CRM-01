from datetime import datetime

from pydantic import BaseModel, Field


class DictionaryBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    is_active: bool = True
    sort_order: int = 100


class CourseCreate(DictionaryBase):
    pass


class SourceCreate(DictionaryBase):
    pass


class StatusCreate(DictionaryBase):
    code: str = Field(min_length=2, max_length=64)
    is_final: bool = False


class CourseRead(DictionaryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SourceRead(DictionaryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StatusRead(StatusCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
