from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Course, Source, Status

DictionaryModel = TypeVar("DictionaryModel", Course, Source, Status)


async def list_courses(db: AsyncSession, include_inactive: bool = False) -> list[Course]:
    query = select(Course).order_by(Course.sort_order, Course.name)
    if not include_inactive:
        query = query.where(Course.is_active.is_(True))
    result = await db.execute(query)
    return list(result.scalars().all())


async def list_sources(db: AsyncSession, include_inactive: bool = False) -> list[Source]:
    query = select(Source).order_by(Source.sort_order, Source.name)
    if not include_inactive:
        query = query.where(Source.is_active.is_(True))
    result = await db.execute(query)
    return list(result.scalars().all())


async def list_statuses(db: AsyncSession, include_inactive: bool = False) -> list[Status]:
    query = select(Status).order_by(Status.sort_order, Status.name)
    if not include_inactive:
        query = query.where(Status.is_active.is_(True))
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_course(
    db: AsyncSession,
    *,
    name: str,
    is_active: bool = True,
    sort_order: int = 100,
) -> Course:
    course = Course(name=name, is_active=is_active, sort_order=sort_order)
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


async def create_source(
    db: AsyncSession,
    *,
    name: str,
    is_active: bool = True,
    sort_order: int = 100,
) -> Source:
    source = Source(name=name, is_active=is_active, sort_order=sort_order)
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


async def create_status(
    db: AsyncSession,
    *,
    code: str,
    name: str,
    is_active: bool = True,
    is_final: bool = False,
    sort_order: int = 100,
) -> Status:
    status = Status(
        code=code,
        name=name,
        is_active=is_active,
        is_final=is_final,
        sort_order=sort_order,
    )
    db.add(status)
    await db.commit()
    await db.refresh(status)
    return status
