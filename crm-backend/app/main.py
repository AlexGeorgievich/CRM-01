from pathlib import Path
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.redis_client import get_redis
from app.api.v1.router import router as v1_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


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

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса."""
    redis = await get_redis()
    await redis.ping()
    async with engine.connect() as connection:
        await connection.execute(text("select 1"))
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "checks": {"database": "ok", "redis": "ok"},
    }
