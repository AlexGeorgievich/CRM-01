import csv
from io import StringIO

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.crud.lead import (
    create_comment,
    create_lead,
    get_lead,
    list_leads_for_export,
    list_comments,
    list_leads,
    soft_delete_lead,
    update_lead,
    validate_lead_references,
)
from app.database import get_db
from app.models import Comment, Lead, User, UserRole
from app.schemas import (
    CommentCreate,
    CommentRead,
    LeadCreate,
    LeadDetail,
    LeadList,
    LeadUpdate,
    Message,
)

router = APIRouter()


def _can_access_lead(current_user: User, lead: Lead) -> bool:
    return current_user.role == UserRole.ADMIN.value or lead.assigned_manager_id == current_user.id


def _assert_can_access_lead(current_user: User, lead: Lead) -> None:
    if not _can_access_lead(current_user, lead):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")


def _csv_response(leads: list[Lead]) -> StreamingResponse:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "id",
            "customer_name",
            "contact",
            "email",
            "status",
            "course",
            "source",
            "assigned_manager",
            "next_contact_date",
            "notes",
            "created_at",
            "updated_at",
        ]
    )
    for lead in leads:
        writer.writerow(
            [
                lead.id,
                lead.customer_name,
                lead.contact,
                lead.email or "",
                lead.status.name,
                lead.course.name if lead.course else "",
                lead.source.name if lead.source else "",
                lead.assigned_manager.full_name if lead.assigned_manager else "",
                lead.next_contact_date.isoformat() if lead.next_contact_date else "",
                lead.notes or "",
                lead.created_at.isoformat(),
                lead.updated_at.isoformat(),
            ]
        )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=leads.csv"},
    )


@router.get("", response_model=LeadList)
async def read_leads(
    status_id: int | None = None,
    course_id: int | None = None,
    source_id: int | None = None,
    assigned_manager_id: int | None = None,
    search: str | None = None,
    overdue: bool = False,
    include_deleted: bool = False,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadList:
    items, total = await list_leads(
        db,
        status_id=status_id,
        course_id=course_id,
        source_id=source_id,
        assigned_manager_id=assigned_manager_id,
        search=search,
        overdue=overdue,
        include_deleted=include_deleted,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )
    return LeadList(items=items, total=total, skip=skip, limit=limit)


@router.get("/export.csv")
async def export_leads_csv(
    status_id: int | None = None,
    course_id: int | None = None,
    source_id: int | None = None,
    assigned_manager_id: int | None = None,
    search: str | None = None,
    overdue: bool = False,
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
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
    return _csv_response(leads)


@router.post("/import.csv")
async def import_leads_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    raw = await file.read()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(StringIO(text))
    created = 0
    errors: list[dict] = []

    for row_number, row in enumerate(reader, start=2):
        try:
            status_id = int(row.get("status_id") or 0)
            payload = LeadCreate(
                customer_name=row.get("customer_name") or "",
                contact=row.get("contact") or "",
                email=row.get("email") or None,
                notes=row.get("notes") or None,
                course_id=int(row["course_id"]) if row.get("course_id") else None,
                source_id=int(row["source_id"]) if row.get("source_id") else None,
                status_id=status_id,
                assigned_manager_id=int(row["assigned_manager_id"]) if row.get("assigned_manager_id") else None,
                next_contact_date=row.get("next_contact_date") or None,
            )
            reference_errors = await validate_lead_references(db, payload=payload)
            if reference_errors:
                errors.append({"row": row_number, "errors": reference_errors})
                continue
            await create_lead(db, payload=payload, current_user=current_user)
            created += 1
        except Exception as exc:  # noqa: BLE001 - row-level import report
            errors.append({"row": row_number, "errors": {"row": str(exc)}})

    return {"created": created, "errors": errors}


@router.post("", response_model=LeadDetail, status_code=status.HTTP_201_CREATED)
async def create_new_lead(
    payload: LeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Lead:
    if current_user.role == UserRole.MANAGER.value:
        if payload.assigned_manager_id not in (None, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers can assign leads only to themselves",
            )
        payload = payload.model_copy(update={"assigned_manager_id": current_user.id})
    errors = await validate_lead_references(db, payload=payload)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=errors,
        )
    return await create_lead(db, payload=payload, current_user=current_user)


@router.get("/{lead_id}", response_model=LeadDetail)
async def read_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Lead:
    lead = await get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    _assert_can_access_lead(current_user, lead)
    return lead


@router.patch("/{lead_id}", response_model=LeadDetail)
async def update_existing_lead(
    lead_id: int,
    payload: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Lead:
    lead = await get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    _assert_can_access_lead(current_user, lead)
    if (
        current_user.role == UserRole.MANAGER.value
        and payload.assigned_manager_id is not None
        and payload.assigned_manager_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can assign leads only to themselves",
        )
    errors = await validate_lead_references(db, payload=payload, partial=True)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=errors,
        )
    return await update_lead(db, lead=lead, payload=payload, current_user=current_user)


@router.delete("/{lead_id}", response_model=Message)
async def delete_existing_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Message:
    lead = await get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    _assert_can_access_lead(current_user, lead)
    await soft_delete_lead(db, lead=lead, current_user=current_user)
    return Message(message="Lead deleted")


@router.get("/{lead_id}/comments", response_model=list[CommentRead])
async def read_lead_comments(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Comment]:
    lead = await get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    _assert_can_access_lead(current_user, lead)
    return await list_comments(db, lead_id)


@router.post(
    "/{lead_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead_comment(
    lead_id: int,
    payload: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Comment:
    lead = await get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    _assert_can_access_lead(current_user, lead)
    return await create_comment(
        db,
        lead_id=lead_id,
        author_id=current_user.id,
        body=payload.body,
    )
