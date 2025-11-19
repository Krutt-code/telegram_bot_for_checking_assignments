import traceback
from pprint import pformat
from typing import Optional

from redis.asyncio import Redis

from src.redis_cache import redis_cache_logger


class RedisClient:
    def __init__(self, redis_url: str) -> None:
        self.redis_url = redis_url
        self.redis: Optional[Redis] = None
        self._logger = redis_cache_logger.get_class_logger(self)

    async def connect(self):
        self.redis = Redis.from_url(self.redis_url)
        await self.redis.ping()

    async def close(self):
        if isinstance(self.redis, Redis):
            await self.redis.close()
        self.redis = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            error_details = {
                "type": exc_type.__name__,
                "value": str(exc_val),
                "traceback": traceback.format_exc(),
            }
            error_details_text = pformat(error_details, indent=4)
            self._logger.critical(f"Произошла ошибка:\n{error_details_text}")
        await self.close()

    async def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        value = await self.redis.get(key)
        return value.decode() if value is not None else default

    async def set(self, key: str, value: str, expire: int = 0) -> None:
        await self.redis.set(key, value, ex=expire)

    async def scan_keys(self, pattern: str) -> list:
        keys = []
        cursor = b"0"
        while cursor:
            cursor, found_keys = await self.redis.scan(cursor=cursor, match=pattern)
            keys.extend(found_keys)
        return keys

    async def delete(self, *names: str) -> list:
        return await self.redis.delete(*names)


""" Тесты

async with RedisClient(settings.redis_url) as redis_client:
    print(await redis_client.get("test"))
    await redis_client.set("test", "test, тест, 1234", 10)
    print(await redis_client.get("test"))
    await asyncio.sleep(10)
    print("После 10 сек", await redis_client.get("test"))
"""
