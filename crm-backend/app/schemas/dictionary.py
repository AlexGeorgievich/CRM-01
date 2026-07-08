from datetime import datetime

from pydantic import BaseModel, Field


class DictionaryBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    is_active: bool = True
    sort_order: int = 100


class CourseCreate(DictionaryBase):
    pass


class CourseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None
    sort_order: int | None = None


class SourceCreate(DictionaryBase):
    pass


class SourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None
    sort_order: int | None = None


class StatusCreate(DictionaryBase):
    code: str = Field(min_length=2, max_length=64)
    is_final: bool = False


class StatusUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, min_length=2, max_length=64)
    is_active: bool | None = None
    sort_order: int | None = None
    is_final: bool | None = None


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
