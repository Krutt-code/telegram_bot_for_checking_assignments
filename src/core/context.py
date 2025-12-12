from __future__ import annotations

from dataclasses import dataclass

from src.core.settings import settings
from src.redis import RedisClient, RedisStateClient
from src.services import AdminStorage, RoleStorage


@dataclass(slots=True)
class AppContext:
    """
    Контейнер зависимостей приложения (инфраструктура/сервисы).

    Идея: создать один раз на старте и прокинуть в aiogram через middleware,
    чтобы хендлеры/фильтры получали зависимости через injection, без "протаскивания".
    """

    redis: RedisClient
    redis_state: RedisStateClient
    admin_storage: AdminStorage
    role_storage: RoleStorage

    @classmethod
    async def create(cls) -> "AppContext":
        redis = RedisClient(settings.redis_url)
        await redis.connect()
        return cls(
            redis=redis,
            redis_state=RedisStateClient(redis),
            admin_storage=AdminStorage(redis),
            role_storage=RoleStorage(redis),
        )

    async def close(self) -> None:
        await self.redis.close()
