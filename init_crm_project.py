#!/usr/bin/env python3
"""
Скрипт инициализации структуры проекта CRM-минисистемы.
Создаёт все каталоги, файлы с базовым содержимым,
готовые к запуску через Docker Compose.
"""

import os
import stat
from pathlib import Path

# ---------- Конфигурация ----------
PROJECT_NAME = "crm-backend"
BASE_DIR = Path.cwd() / PROJECT_NAME

# Шаблоны содержимого файлов (ключ - относительный путь)
FILES = {}

# ---------- Вспомогательные функции ----------
def write_file(path: Path, content: str, executable: bool = False):
    """Создать файл с содержимым, при необходимости сделать исполняемым."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    if executable:
        # Добавить права на исполнение для владельца
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IXUSR)

# ---------- 1. Корневые файлы ----------
FILES[".env.example"] = """# APP
APP_NAME=CRM-MiniSystem
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# DATABASE (PostgreSQL)
POSTGRES_USER=crm_user
POSTGRES_PASSWORD=crm_password
POSTGRES_DB=crm_db
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}

# REDIS
REDIS_URL=redis://redis:6379/0

# AUTH
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
"""

FILES[".gitignore"] = """__pycache__/
*.pyc
.env
.venv
*.db
*.sqlite3
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
/logs/
/static/
/media/
.DS_Store
*.log
"""

FILES["docker-compose.yml"] = """version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: crm_postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-crm_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-crm_password}
      POSTGRES_DB: ${POSTGRES_DB:-crm_db}
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
    networks:
      - crm_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-crm_user}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: crm_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - crm_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    container_name: crm_app
    env_file:
      - .env
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - .:/app
    networks:
      - crm_network
    entrypoint: ["/app/entrypoint.sh"]

volumes:
  pg_data:
  redis_data:

networks:
  crm_network:
    driver: bridge
"""

FILES["Dockerfile"] = """FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей (для psycopg2, netcat и пр.)
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    libpq-dev \\
    netcat-openbsd \\
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Делаем entrypoint исполняемым
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
"""

FILES["entrypoint.sh"] = """#!/bin/sh
set -e

# Ожидание PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "PostgreSQL started"

# Применение миграций
echo "Running migrations..."
alembic upgrade head

# Запуск приложения
echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

FILES["requirements.txt"] = """fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
asyncpg==0.30.0
alembic==1.14.1
pydantic==2.10.4
pydantic-settings==2.6.1
python-dotenv==1.0.1
redis==5.2.1
bcrypt==4.2.1
python-multipart==0.0.20
"""

FILES["alembic.ini"] = """[alembic]
script_location = app/migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = %(DATABASE_URL)s

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 88

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

FILES["README.md"] = """# CRM-MiniSystem Backend

## Запуск разработки

1. Клонировать репозиторий
2. Скопировать `.env.example` в `.env` и заполнить (секретные ключи)
3. Запустить Docker: `docker-compose up -d`
4. Приложение доступно по адресу: http://localhost:8000
5. Документация API: http://localhost:8000/docs

## Команды

- Остановка: `docker-compose down`
- Просмотр логов: `docker-compose logs -f app`
- Создание миграции: `docker-compose exec app alembic revision --autogenerate -m "message"`
- Применение миграций: `docker-compose exec app alembic upgrade head`
"""

# ---------- 2. Файлы приложения (app/) ----------
FILES["app/__init__.py"] = ""

FILES["app/main.py"] = '''import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from app.config import settings
from app.database import engine
from app.redis_client import get_redis
from app.api.v1 import router as v1_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом: подключение к Redis и т.п."""
    # Старт
    redis = await get_redis()
    await redis.ping()
    logger.info("Redis connected")
    yield
    # Завершение
    await engine.dispose()
    await redis.close()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS (для разработки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров версии v1
app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса."""
    redis = await get_redis()
    await redis.ping()
    # Проверка БД через простой запрос (будет добавлено позже)
    return {"status": "ok", "service": settings.APP_NAME}
'''

FILES["app/config.py"] = '''from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "CRM-MiniSystem"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: SecretStr = Field(default="change-me-in-production", min_length=32)

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://crm_user:crm_password@postgres:5432/crm_db"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Auth
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"


settings = AppSettings()
'''

FILES["app/database.py"] = '''from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.config import settings

# Движок с настройками пула
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для моделей
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency для получения сессии БД."""
    async with AsyncSessionLocal() as session:
        yield session
'''

FILES["app/redis_client.py"] = '''from redis.asyncio import Redis, from_url
from app.config import settings

_redis_client: Redis | None = None


async def get_redis() -> Redis:
    """Возвращает синглтон-клиент Redis."""
    global _redis_client
    if _redis_client is None:
        _redis_client = from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def set_key(key: str, value: str, expire: int = None) -> None:
    redis = await get_redis()
    await redis.set(key, value, ex=expire)


async def get_key(key: str) -> str | None:
    redis = await get_redis()
    return await redis.get(key)


async def delete_key(key: str) -> None:
    redis = await get_redis()
    await redis.delete(key)


async def exists(key: str) -> bool:
    redis = await get_redis()
    return await redis.exists(key) > 0
'''

FILES["app/models/__init__.py"] = "from app.models.base import Base"
FILES["app/models/base.py"] = '''from sqlalchemy import Column, DateTime, Integer, func
from app.database import Base


class TimestampMixin:
    """Миксин с полями created_at и updated_at."""
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
'''

FILES["app/schemas/__init__.py"] = ""
FILES["app/crud/__init__.py"] = ""
FILES["app/api/__init__.py"] = ""
FILES["app/api/v1/__init__.py"] = ""

FILES["app/api/v1/router.py"] = '''from fastapi import APIRouter
# Импортируем роутеры из модулей (пока заглушки)
# from app.api.v1 import leads, auth, users, dictionaries

router = APIRouter()

# router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# router.include_router(leads.router, prefix="/leads", tags=["Leads"])
# router.include_router(users.router, prefix="/users", tags=["Users"])
# router.include_router(dictionaries.router, prefix="/dictionaries", tags=["Dictionaries"])

@router.get("/ping")
async def ping():
    return {"message": "pong"}
'''

FILES["app/api/deps.py"] = '''from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
# from app.crud.user import get_user_by_id

async def get_current_user(
    # Здесь будет логика извлечения пользователя из JWT или сессии
    db: AsyncSession = Depends(get_db),
):
    # Заглушка — возвращаем тестового пользователя
    # В реальности проверить токен и найти пользователя
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required (заглушка)",
    )
    # return None
'''

# ---------- 3. Тесты ----------
FILES["tests/__init__.py"] = ""
FILES["tests/conftest.py"] = '''import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.database import Base, get_db
from app.main import app

# Настройка тестовой БД (in-memory или отдельная)
# @pytest.fixture
# async def db_session():
#     engine = create_async_engine("sqlite+aiosqlite:///test.db")
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     async_session = async_sessionmaker(engine, expire_on_commit=False)
#     async with async_session() as session:
#         yield session
#     await engine.dispose()
'''

# ---------- 4. Создание структуры ----------
def create_project():
    print(f"🔨 Создаём проект в {BASE_DIR}")
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    for rel_path, content in FILES.items():
        file_path = BASE_DIR / rel_path
        write_file(file_path, content)
        print(f"   ✅ {rel_path}")

    # Отдельно делаем entrypoint.sh исполняемым
    entrypoint_path = BASE_DIR / "entrypoint.sh"
    if entrypoint_path.exists():
        st = os.stat(entrypoint_path)
        os.chmod(entrypoint_path, st.st_mode | stat.S_IXUSR)
        print("   🔧 entrypoint.sh сделан исполняемым")

    # Создаём пустую папку для миграций (Alembic)
    migrations_dir = BASE_DIR / "app" / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    (migrations_dir / "versions").mkdir(exist_ok=True)
    (migrations_dir / "__init__.py").touch()

    print("\n✅ Структура проекта успешно создана!")
    print(f"📁 Перейдите в папку: cd {PROJECT_NAME}")
    print("📝 Скопируйте .env.example в .env и заполните переменные")
    print("🐳 Запустите: docker-compose up -d")
    print("🌐 Документация API будет доступна по адресу http://localhost:8000/docs")


if __name__ == "__main__":
    create_project()
    