from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.crud.user import create_user, get_user_by_id, list_users, reset_user_password, update_user
from app.database import get_db
from app.models import User, UserRole
from app.schemas import PasswordReset, UserCreate, UserRead, UserUpdate

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


@router.patch("/{user_id}", response_model=UserRead)
async def update_existing_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> User:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    changes = payload.model_dump(exclude_unset=True)
    if "role" in changes and changes["role"] not in {UserRole.ADMIN.value, UserRole.MANAGER.value}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="role must be admin or manager",
        )
    try:
        return await update_user(db, user=user, changes=changes)
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username or email already exists",
        ) from exc


@router.post("/{user_id}/reset-password", response_model=UserRead)
async def reset_existing_user_password(
    user_id: int,
    payload: PasswordReset,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> User:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return await reset_user_password(db, user=user, password=payload.password)
