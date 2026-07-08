import asyncio

from sqlalchemy import select

from app.config import settings
from app.crud.user import create_user, get_user_by_username
from app.database import AsyncSessionLocal
from app.models import Course, Source, Status, UserRole


async def seed_dictionaries() -> None:
    async with AsyncSessionLocal() as db:
        for model, values in (
            (
                Course,
                [
                    {"name": "Python-разработчик", "sort_order": 10},
                    {"name": "Frontend-разработчик", "sort_order": 20},
                    {"name": "Аналитик данных", "sort_order": 30},
                ],
            ),
            (
                Source,
                [
                    {"name": "Сайт", "sort_order": 10},
                    {"name": "Мессенджер", "sort_order": 20},
                    {"name": "Реклама", "sort_order": 30},
                ],
            ),
        ):
            existing = await db.execute(select(model.id))
            if existing.first() is not None:
                continue
            db.add_all(model(**value) for value in values)

        existing_statuses = await db.execute(select(Status.id))
        if existing_statuses.first() is None:
            db.add_all(
                [
                    Status(code="new", name="Новая", sort_order=10),
                    Status(code="in_progress", name="В работе", sort_order=20),
                    Status(code="paid", name="Оплачено", is_final=True, sort_order=30),
                    Status(code="lost", name="Отказ", is_final=True, sort_order=40),
                ]
            )

        await db.commit()


async def seed_admin() -> None:
    async with AsyncSessionLocal() as db:
        user = await get_user_by_username(db, settings.INITIAL_ADMIN_USERNAME)
        if user is not None:
            return
        await create_user(
            db,
            username=settings.INITIAL_ADMIN_USERNAME,
            password=settings.INITIAL_ADMIN_PASSWORD.get_secret_value(),
            full_name=settings.INITIAL_ADMIN_FULL_NAME,
            email=settings.INITIAL_ADMIN_EMAIL,
            role=UserRole.ADMIN.value,
        )


async def main() -> None:
    await seed_dictionaries()
    await seed_admin()


if __name__ == "__main__":
    asyncio.run(main())
