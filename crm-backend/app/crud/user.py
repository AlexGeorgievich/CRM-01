from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models import User, UserRole


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def list_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).order_by(User.full_name))
    return list(result.scalars().all())


async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str,
) -> User | None:
    user = await get_user_by_username(db, username)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_user(
    db: AsyncSession,
    *,
    username: str,
    password: str,
    full_name: str,
    email: str | None = None,
    role: str = UserRole.MANAGER.value,
    is_active: bool = True,
) -> User:
    user = User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        role=role,
        is_active=is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(
    db: AsyncSession,
    *,
    user: User,
    changes: dict,
) -> User:
    for field, value in changes.items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def reset_user_password(
    db: AsyncSession,
    *,
    user: User,
    password: str,
) -> User:
    user.hashed_password = get_password_hash(password)
    await db.commit()
    await db.refresh(user)
    return user
