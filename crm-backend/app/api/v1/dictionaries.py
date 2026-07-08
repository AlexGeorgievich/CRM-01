from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.crud.dictionary import (
    create_course,
    create_source,
    create_status,
    list_courses,
    list_sources,
    list_statuses,
)
from app.database import get_db
from app.models import Course, Source, Status, User
from app.schemas import (
    CourseCreate,
    CourseRead,
    SourceCreate,
    SourceRead,
    StatusCreate,
    StatusRead,
)

router = APIRouter()


@router.get("/courses", response_model=list[CourseRead])
async def read_courses(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Course]:
    return await list_courses(db)


@router.post("/courses", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
async def create_new_course(
    payload: CourseCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> Course:
    return await create_course(db, **payload.model_dump())


@router.get("/sources", response_model=list[SourceRead])
async def read_sources(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Source]:
    return await list_sources(db)


@router.post("/sources", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
async def create_new_source(
    payload: SourceCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> Source:
    return await create_source(db, **payload.model_dump())


@router.get("/statuses", response_model=list[StatusRead])
async def read_statuses(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Status]:
    return await list_statuses(db)


@router.post("/statuses", response_model=StatusRead, status_code=status.HTTP_201_CREATED)
async def create_new_status(
    payload: StatusCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> Status:
    return await create_status(db, **payload.model_dump())
