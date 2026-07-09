from datetime import date, datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Comment, Course, Lead, Source, Status, User, UserRole
from app.schemas.lead import LeadCreate, LeadUpdate


def _lead_options():
    return (
        selectinload(Lead.course),
        selectinload(Lead.source),
        selectinload(Lead.status),
        selectinload(Lead.assigned_manager),
        selectinload(Lead.created_by),
    )


def _lead_detail_options():
    return (*_lead_options(), selectinload(Lead.comments).selectinload(Comment.author))


def _apply_filters(
    query,
    *,
    status_id: int | None = None,
    course_id: int | None = None,
    source_id: int | None = None,
    assigned_manager_id: int | None = None,
    search: str | None = None,
    include_deleted: bool = False,
    overdue: bool = False,
    current_user: User | None = None,
):
    if current_user and current_user.role == UserRole.MANAGER.value:
        query = query.where(Lead.assigned_manager_id == current_user.id)
    if not include_deleted:
        query = query.where(Lead.deleted_at.is_(None))
    if status_id is not None:
        query = query.where(Lead.status_id == status_id)
    if course_id is not None:
        query = query.where(Lead.course_id == course_id)
    if source_id is not None:
        query = query.where(Lead.source_id == source_id)
    if assigned_manager_id is not None:
        query = query.where(Lead.assigned_manager_id == assigned_manager_id)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(
            or_(
                Lead.customer_name.ilike(like),
                Lead.contact.ilike(like),
                Lead.email.ilike(like),
                Lead.notes.ilike(like),
            )
        )
    if overdue:
        query = query.join(Lead.status).where(
            Lead.next_contact_date.is_not(None),
            Lead.next_contact_date < date.today(),
            Status.is_final.is_(False),
        )
    return query


async def list_leads(
    db: AsyncSession,
    *,
    status_id: int | None = None,
    course_id: int | None = None,
    source_id: int | None = None,
    assigned_manager_id: int | None = None,
    search: str | None = None,
    overdue: bool = False,
    include_deleted: bool = False,
    current_user: User | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Lead], int]:
    base_query = _apply_filters(
        select(Lead),
        status_id=status_id,
        course_id=course_id,
        source_id=source_id,
        assigned_manager_id=assigned_manager_id,
        search=search,
        overdue=overdue,
        include_deleted=include_deleted,
        current_user=current_user,
    )
    count_query = _apply_filters(
        select(func.count(Lead.id)),
        status_id=status_id,
        course_id=course_id,
        source_id=source_id,
        assigned_manager_id=assigned_manager_id,
        search=search,
        overdue=overdue,
        include_deleted=include_deleted,
        current_user=current_user,
    )

    total = await db.scalar(count_query)
    result = await db.execute(
        base_query.options(*_lead_options())
        .order_by(Lead.created_at.desc(), Lead.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all()), int(total or 0)


async def list_leads_for_export(
    db: AsyncSession,
    *,
    status_id: int | None = None,
    course_id: int | None = None,
    source_id: int | None = None,
    assigned_manager_id: int | None = None,
    search: str | None = None,
    overdue: bool = False,
    include_deleted: bool = False,
    current_user: User | None = None,
) -> list[Lead]:
    query = _apply_filters(
        select(Lead),
        status_id=status_id,
        course_id=course_id,
        source_id=source_id,
        assigned_manager_id=assigned_manager_id,
        search=search,
        overdue=overdue,
        include_deleted=include_deleted,
        current_user=current_user,
    )
    result = await db.execute(
        query.options(*_lead_options()).order_by(Lead.created_at.desc(), Lead.id.desc())
    )
    return list(result.scalars().all())


async def get_lead(db: AsyncSession, lead_id: int) -> Lead | None:
    result = await db.execute(
        select(Lead)
        .where(Lead.id == lead_id, Lead.deleted_at.is_(None))
        .options(*_lead_detail_options())
    )
    return result.scalar_one_or_none()


async def create_lead(
    db: AsyncSession,
    *,
    payload: LeadCreate,
    current_user: User,
) -> Lead:
    lead = Lead(**payload.model_dump(), created_by_id=current_user.id)
    db.add(lead)
    await db.flush()
    db.add(
        Comment(
            lead_id=lead.id,
            author_id=current_user.id,
            body="Заявка создана",
            is_system=True,
        )
    )
    await db.commit()
    return await get_lead(db, lead.id)  # type: ignore[return-value]


async def validate_lead_references(
    db: AsyncSession,
    *,
    payload: LeadCreate | LeadUpdate,
    partial: bool = False,
) -> dict[str, str]:
    data = payload.model_dump(exclude_unset=partial)
    errors: dict[str, str] = {}

    async def exists(model, item_id: int) -> bool:
        result = await db.execute(
            select(model.id).where(model.id == item_id, model.is_active.is_(True))
        )
        return result.scalar_one_or_none() is not None

    if "status_id" in data:
        if data["status_id"] is None:
            errors["status_id"] = "Status is required"
        elif not await exists(Status, data["status_id"]):
            errors["status_id"] = "Status does not exist or is inactive"

    if data.get("course_id") is not None and not await exists(Course, data["course_id"]):
        errors["course_id"] = "Course does not exist or is inactive"

    if data.get("source_id") is not None and not await exists(Source, data["source_id"]):
        errors["source_id"] = "Source does not exist or is inactive"

    if data.get("assigned_manager_id") is not None:
        result = await db.execute(
            select(User.id).where(
                User.id == data["assigned_manager_id"],
                User.is_active.is_(True),
            )
        )
        if result.scalar_one_or_none() is None:
            errors["assigned_manager_id"] = "Assigned manager does not exist or is inactive"

    return errors


async def update_lead(
    db: AsyncSession,
    *,
    lead: Lead,
    payload: LeadUpdate,
    current_user: User,
) -> Lead:
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(lead, field, value)
    if changes:
        db.add(
            Comment(
                lead_id=lead.id,
                author_id=current_user.id,
                body=f"Заявка обновлена: {', '.join(sorted(changes.keys()))}",
                is_system=True,
            )
        )
    await db.commit()
    return await get_lead(db, lead.id)  # type: ignore[return-value]


async def soft_delete_lead(
    db: AsyncSession,
    *,
    lead: Lead,
    current_user: User,
) -> None:
    lead.deleted_at = datetime.now(timezone.utc)
    db.add(
        Comment(
            lead_id=lead.id,
            author_id=current_user.id,
            body="Заявка удалена",
            is_system=True,
        )
    )
    await db.commit()


async def list_comments(db: AsyncSession, lead_id: int) -> list[Comment]:
    result = await db.execute(
        select(Comment)
        .where(Comment.lead_id == lead_id)
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at.asc(), Comment.id.asc())
    )
    return list(result.scalars().all())


async def create_comment(
    db: AsyncSession,
    *,
    lead_id: int,
    author_id: int,
    body: str,
) -> Comment:
    comment = Comment(lead_id=lead_id, author_id=author_id, body=body)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    result = await db.execute(
        select(Comment)
        .where(Comment.id == comment.id)
        .options(selectinload(Comment.author))
    )
    return result.scalar_one()
