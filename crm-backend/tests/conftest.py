from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.security import get_password_hash
from app.database import get_db
from app.main import app
from app.models import Base, Course, Source, Status, User, UserRole


@pytest.fixture()
async def async_session_factory(tmp_path):
    db_path = tmp_path / "test_crm.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        session.add_all(
            [
                Status(code="new", name="Новая", sort_order=10),
                Status(code="in_progress", name="В работе", sort_order=20),
                Status(code="paid", name="Оплачено", is_final=True, sort_order=30),
                Course(name="Python-разработчик", sort_order=10),
                Source(name="Сайт", sort_order=10),
                User(
                    username="admin",
                    email="admin@example.local",
                    full_name="CRM Administrator",
                    hashed_password=get_password_hash("admin12345"),
                    role=UserRole.ADMIN.value,
                    is_active=True,
                ),
                User(
                    username="manager",
                    email="manager@example.local",
                    full_name="CRM Manager",
                    hashed_password=get_password_hash("manager12345"),
                    role=UserRole.MANAGER.value,
                    is_active=True,
                ),
            ]
        )
        await session.commit()

    yield session_factory

    await engine.dispose()


@pytest.fixture()
def client(async_session_factory) -> Generator[TestClient, None, None]:
    async def override_get_db() -> AsyncGenerator:
        async with async_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
