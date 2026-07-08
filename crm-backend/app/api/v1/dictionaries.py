from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.crud.dictionary import (
    create_course,
    create_source,
    create_status,
    get_dictionary_item,
    list_courses,
    list_sources,
    list_statuses,
    update_dictionary_item,
)
from app.database import get_db
from app.models import Course, Source, Status, User
from app.schemas import (
    CourseCreate,
    CourseRead,
    CourseUpdate,
    SourceCreate,
    SourceRead,
    SourceUpdate,
    StatusCreate,
    StatusRead,
    StatusUpdate,
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


@router.patch("/courses/{course_id}", response_model=CourseRead)
async def update_existing_course(
    course_id: int,
    payload: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> Course:
    course = await get_dictionary_item(db, Course, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return await update_dictionary_item(
        db,
        item=course,
        changes=payload.model_dump(exclude_unset=True),
    )


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


@router.patch("/sources/{source_id}", response_model=SourceRead)
async def update_existing_source(
    source_id: int,
    payload: SourceUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> Source:
    source = await get_dictionary_item(db, Source, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return await update_dictionary_item(
        db,
        item=source,
        changes=payload.model_dump(exclude_unset=True),
    )


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


@router.patch("/statuses/{status_id}", response_model=StatusRead)
async def update_existing_status(
    status_id: int,
    payload: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> Status:
    crm_status = await get_dictionary_item(db, Status, status_id)
    if crm_status is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    return await update_dictionary_item(
        db,
        item=crm_status,
        changes=payload.model_dump(exclude_unset=True),
    )
