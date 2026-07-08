from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.dictionary import list_courses, list_sources, list_statuses
from app.crud.lead import list_leads_for_export
from app.crud.user import list_users
from app.database import get_db
from app.models import Lead, User, UserRole

router = APIRouter()


def _is_overdue(lead: Lead) -> bool:
    return bool(
        lead.next_contact_date
        and lead.next_contact_date < date.today()
        and not lead.status.is_final
    )


@router.get("/summary")
async def read_summary(
    status_id: int | None = None,
    course_id: int | None = None,
    source_id: int | None = None,
    assigned_manager_id: int | None = None,
    search: str | None = None,
    overdue: bool = False,
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    leads = await list_leads_for_export(
        db,
        status_id=status_id,
        course_id=course_id,
        source_id=source_id,
        assigned_manager_id=assigned_manager_id,
        search=search,
        overdue=overdue,
        include_deleted=include_deleted,
        current_user=current_user,
    )
    statuses = await list_statuses(db)
    courses = await list_courses(db)
    sources = await list_sources(db)
    users = await list_users(db) if current_user.role == UserRole.ADMIN.value else [current_user]

    active_leads = [lead for lead in leads if lead.deleted_at is None]
    won = sum(1 for lead in active_leads if lead.status.code in {"won", "paid"})
    overdue_count = sum(1 for lead in active_leads if _is_overdue(lead))
    conversion = round(won / len(active_leads) * 100) if active_leads else 0

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "kpi": {
            "total": len(active_leads),
            "won": won,
            "overdue": overdue_count,
            "conversion": conversion,
        },
        "by_status": [
            {
                "id": status.id,
                "name": status.name,
                "code": status.code,
                "value": sum(1 for lead in active_leads if lead.status_id == status.id),
            }
            for status in statuses
        ],
        "by_source": [
            {
                "id": source.id,
                "name": source.name,
                "leads": sum(1 for lead in active_leads if lead.source_id == source.id),
                "won": sum(
                    1
                    for lead in active_leads
                    if lead.source_id == source.id and lead.status.code in {"won", "paid"}
                ),
            }
            for source in sources
        ],
        "by_course": [
            {
                "id": course.id,
                "name": course.name,
                "leads": sum(1 for lead in active_leads if lead.course_id == course.id),
            }
            for course in courses
        ],
        "by_manager": [
            {
                "id": user.id,
                "name": user.full_name,
                "leads": sum(1 for lead in active_leads if lead.assigned_manager_id == user.id),
                "overdue": sum(
                    1
                    for lead in active_leads
                    if lead.assigned_manager_id == user.id and _is_overdue(lead)
                ),
                "won": sum(
                    1
                    for lead in active_leads
                    if lead.assigned_manager_id == user.id and lead.status.code in {"won", "paid"}
                ),
            }
            for user in users
            if user.role == UserRole.MANAGER.value
        ],
    }
