from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.crud.user import create_user, list_users
from app.database import get_db
from app.models import User, UserRole
from app.schemas import UserCreate, UserRead

router = APIRouter()


@router.get("", response_model=list[UserRead])
async def read_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[User]:
    return await list_users(db)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> User:
    if payload.role not in {UserRole.ADMIN.value, UserRole.MANAGER.value}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="role must be admin or manager",
        )
    try:
        return await create_user(
            db,
            username=payload.username,
            password=payload.password,
            full_name=payload.full_name,
            email=payload.email,
            role=payload.role,
            is_active=payload.is_active,
        )
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username or email already exists",
        ) from exc
