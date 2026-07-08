from redis.asyncio import Redis, from_url
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
